import duckdb
import pandas as pd
from pydantic import BaseModel, Field, ValidationError
import ollama
import time
import csv
import json

# ============================================================
# 1. PYDANTIC-SCHEMA
# ============================================================
class DublettenEntscheidung(BaseModel):
    is_duplicate: bool = Field(description="Sind die beiden Datensätze dieselbe reale Person/Tier?")
    confidence: float = Field(description="Sicherheit der Entscheidung von 0.0 (unsicher) bis 1.0 (absolut sicher).")
    reasoning: str = Field(description="Freitext, 1-2 Sätze Begründung für die Entscheidung.")
    decisive_signal: Literal["name", "address", "phone", "email", "combined"] = Field(
        description="Welches Merkmal war am wichtigsten für die Entscheidung?"
    )

# ============================================================
# 2. PROMPT-KONFIGURATION
# ============================================================
SYSTEM_PROMPT = """Du bist ein hochpräziser Daten-Analyst für Tierarztpraxen. Deine Aufgabe ist es, zu entscheiden, ob zwei Kundendatensätze dieselbe reale Person.

Namensabgleich: Berücksichtige Tippfehler und phonetische Ähnlichkeiten. Bleibe bei Namensgleichheit skeptisch und prüfe die Adresse (PLZ/Straße) als primäres Merkmal.

Logische Widersprüche: Unterschiedliche PLZ oder Straßen sind klare Ausschlusskriterien (nach Bereinigung von Zifferndrehern). Identische Namen an völlig verschiedenen Wohnorten sind keine Dubletten.

Kontaktdaten: Leicht abweichende Telefonnummern oder E-Mails sind allein kein Ausschlusskriterium, da Personen mehrere Kontakte besitzen können. Stammdaten (Name/Adresse) sind hier höher zu gewichten.

Fehlwerte: Bestrafe NULL-Werte nicht. Gewichte bei fehlenden Informationen die übereinstimmenden Stammdaten (Name/Adresse) stärker.

Antworte strikt im JSON-Format gemäß dem vorgegebenen Schema."""

# ============================================================
# 3. LLM-LOGIK MIT RETRY 
# ============================================================
def klassifiziere(a_text, b_text):
    prompt = f"Datensatz A: {a_text}\nDatensatz B: {b_text}"
    
    for versuch in range(1): # Max 1 Versuche bei Fehlern
        try:
            response = ollama.chat(
                model='qwen2.5:7b',
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                format=DublettenEntscheidung.model_json_schema(),
                options={"temperature": 0.0}
            )
            return DublettenEntscheidung.model_validate_json(response['message']['content'])
        except (ValidationError, json.JSONDecodeError):
            time.sleep(1)
            continue
    return None

# ============================================================
# 4. HAUPTPROGRAMM
# ============================================================
def main():
    print("Starte LLM-Judge (mit Retry-Logik)...")
    con = duckdb.connect("verbund.duckdb")

    # Kandidaten laden (nur die semantisch anspruchsvollen Fälle > 0.0001)
    df_kandidaten = con.execute("""
        SELECT * FROM staging.kandidaten_paare 
        WHERE distanz > 0.0001
        ORDER BY distanz ASC 
        LIMIT 30
    """).df()

    # Match-Tabelle vorbereiten
    con.execute("""
        CREATE OR REPLACE TABLE staging.match_entscheidung (
            praxis_a INTEGER, id_a VARCHAR, praxis_b INTEGER, id_b VARCHAR,
            is_duplicate BOOLEAN, confidence FLOAT, reasoning VARCHAR, signal VARCHAR
        )
    """)

    with open("dubletten_ergebnisse.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Praxis_A", "ID_A", "Praxis_B", "ID_B", "Distanz", "Ist_Dublette", "Sicherheit", "Signal", "Begruendung"])

        for i, row in df_kandidaten.iterrows():
            entscheidung = klassifiziere(row['kunde_a_text'], row['kunde_b_text'])
            
            if entscheidung:
                sicherheit_prozent = int(round(entscheidung.confidence * 100))
                status = "🟢 DUBLETTE" if entscheidung.is_duplicate else "🔴 KEINE DUBLETTE"
                
                # Konsolenausgabe
                print(f"Paar {i+1} | Distanz: {row['distanz']:.4f}")
                print(f"A: {row['kunde_a_text'][:80]}...")
                print(f"B: {row['kunde_b_text'][:80]}...")
                print(f"Urteil: {status} (Sicherheit: {sicherheit_prozent}%)")
                print(f"Begründung: {entscheidung.reasoning}\n" + "-"*50)

                # Speichern
                writer.writerow([row['kunde_a_praxis'], row['kunde_a_id'], row['kunde_b_praxis'], row['kunde_b_id'], 
                                 row['distanz'], entscheidung.is_duplicate, entscheidung.confidence, 
                                 entscheidung.decisive_signal, entscheidung.reasoning])
                
                con.execute("INSERT INTO staging.match_entscheidung VALUES (?,?,?,?,?,?,?,?)", 
                            [row['kunde_a_praxis'], row['kunde_a_id'], row['kunde_b_praxis'], row['kunde_b_id'], 
                             entscheidung.is_duplicate, entscheidung.confidence, entscheidung.reasoning, entscheidung.decisive_signal])
            
            time.sleep(1)

    con.close()
    print("LLM-Matching abgeschlossen.")

if __name__ == "__main__":
    main()
