import duckdb
import pandas as pd
from pydantic import BaseModel, Field
from typing import Literal
import ollama

# PYDANTIC-SCHEMA 
class DublettenEntscheidung(BaseModel):
    is_duplicate: bool = Field(description="Sind die beiden Datensätze dieselbe reale Person/Tier?")
    confidence: float = Field(description="Sicherheit der Entscheidung von 0.0 (unsicher) bis 1.0 (absolut sicher).")
    reasoning: str = Field(description="Freitext, 1-2 Sätze Begründung für die Entscheidung.")
    decisive_signal: Literal["name", "address", "phone", "email", "combined"] = Field(
        description="Welches Merkmal war am wichtigsten für die Entscheidung?"
    )

def hole_kandidaten(con, limit=25):
    """Holt Kandidatenpaare aus der DuckDB """
    kunden = con.execute("SELECT praxis, quell_zeile, quell_text, embedding FROM staging.kunden_embeddings").df()
    
    kandidaten_liste = []
    gesehene_paare = set()

    for index, row in kunden.iterrows():
        # Suche die 10 nächsten Nachbarn pro Kunde
        nachbarn = con.execute(f"""
            SELECT praxis, quell_zeile, quell_text, 
                   list_cosine_distance(embedding, ?::FLOAT[768]) as distanz
            FROM staging.kunden_embeddings
            WHERE NOT (praxis = '{row['praxis']}' AND quell_zeile = {row['quell_zeile']})
            ORDER BY distanz ASC
            LIMIT 10
        """, [row['embedding']]).df()

        for _, nachbar in nachbarn.iterrows():
            if nachbar['distanz'] < 0.15: 
                paar_id = tuple(sorted([f"{row['praxis']}_{row['quell_zeile']}", f"{nachbar['praxis']}_{nachbar['quell_zeile']}"]))
                if paar_id not in gesehene_paare:
                    gesehene_paare.add(paar_id)
                    kandidaten_liste.append({
                        'kunde_a': row['quell_text'],
                        'kunde_b': nachbar['quell_text'],
                        'distanz': nachbar['distanz']
                    })
                    
    # Auf 25 Kandidaten limitieren
    df_kandidaten = pd.DataFrame(kandidaten_liste).sort_values(by='distanz').head(limit)
    return df_kandidaten

def main():
    print("Starte LLM-Judge für Dubletten-Prüfung...")
    
    # Verbindung aufbauen
    con = duckdb.connect("verbund.duckdb")
    con.execute("LOAD vss;")

    try:
        # 1. 25 Kandidaten an das LLM übergeben
        df_kandidaten = hole_kandidaten(con, limit=25)
        print(f"Bewerte die Top {len(df_kandidaten)} Kandidatenpaare mit qwen2.5:7b...\n")
        print("-" * 80)

        # 2. Lokales LLM für jedes Paar befragen
        for i, row in df_kandidaten.iterrows():
            prompt = f"""
            Sind diese beiden Datensätze dieselbe Person/Tier? Antworte mit Begründung.
            Datensatz A: {row['kunde_a']}
            Datensatz B: {row['kunde_b']}
            """

            try:
                # API-Aufruf an das Ollama-Modell
                response = ollama.chat(
                    model='qwen2.5:7b',
                    messages=[
                        {"role": "system", "content": "Du bist ein präziser Daten-Analyst für Tierarztpraxen. Beachte Tippfehler in Namen oder Adressen."},
                        {"role": "user", "content": prompt}
                    ],
                    format=DublettenEntscheidung.model_json_schema(),
                    options={"temperature": 0.0} 
                )
                
                # JSON-Antwort in Pydantic validieren
                entscheidung = DublettenEntscheidung.model_validate_json(response['message']['content'])
                
                print(f"Paar {i+1}:")
                print(f"A: {row['kunde_a'][:80]}...")
                print(f"B: {row['kunde_b'][:80]}...")
                
                status = "🟢 DUBLETTE" if entscheidung.is_duplicate else "🔴​ KEINE DUBLETTE"
                warning = "🟡 HUMAN IN THE LOOP NÖTIG!" if entscheidung.confidence < 0.8 else ""
                
                # Die Confidence wird in % angezeigt
                print(f"Urteil:      {status} (Sicherheit: {entscheidung.confidence}%){warning}")
                print(f"Signal:      {entscheidung.decisive_signal.upper()}")
                print(f"Begründung:  {entscheidung.reasoning}")
                print("-" * 80)
                
            except Exception as e:
                print(f"Fehler bei Paar {i+1}: Konnte Antwort nicht verarbeiten. ({e})")
                
    finally:
        con.close()

if __name__ == "__main__":
    main()
