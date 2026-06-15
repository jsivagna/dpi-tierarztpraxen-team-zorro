import duckdb
import pandas as pd
import requests
import time

# 1. DEINEN NEUEN API-KEY HIER EINTRAGEN
API_KEY = "AQ.Ab8RN6K3Z-Ki54UoRuPn-RFpO4Ks4f9Z7fx_nMp-wFUhTWL1ig"

def lade_kunden(con, praxis_name, tabellen_name):
    """Holt alle Zeilen einer Tabelle und macht einen langen Text-String daraus."""
    df = con.execute(f"SELECT * FROM staging.{tabellen_name}").df()
    kunden = []
    for index, row in df.iterrows():
        row_dict = row.dropna().to_dict()
        quell_zeile = row_dict.pop('quell_zeile', index)
        # Alle Daten zu einem durchsuchbaren Text zusammenkleben
        text_string = " | ".join([f"{k}: {v}" for k, v in row_dict.items()])
        kunden.append({
            'praxis': praxis_name,
            'quell_zeile': int(quell_zeile),
            'quell_text': text_string
        })
    return kunden

def main():
    print("🚀 Starte KI-Embedding-Prozess über direkte REST-API...")
    con = duckdb.connect("verbund.duckdb")

    # 1. Daten sammeln
    print("Sammle Kundendaten aus allen Praxen...")
    alle_kunden = []
    alle_kunden.extend(lade_kunden(con, 'Juckstadt', 'juck_kunden'))
    alle_kunden.extend(lade_kunden(con, 'Waldrand', 'wald_kunden'))
    alle_kunden.extend(lade_kunden(con, 'Schmidt', 'schm_kunden'))
    alle_kunden.extend(lade_kunden(con, 'Bergblick', 'berg_patienten'))
    
    df_kunden = pd.DataFrame(alle_kunden)
    print(f"Insgesamt {len(df_kunden)} Kunden gefunden.")

    # 2. Embeddings via direktem HTTP-Request abrufen
    print("Sende Daten an Google Gemini zur Vektor-Berechnung (das dauert ca. 10-20 Sekunden)...")
    texte = df_kunden['quell_text'].tolist()
    alle_embeddings = []
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:batchEmbedContents?key={API_KEY}"
    batch_size = 100
    
    for i in range(0, len(texte), batch_size):
        batch = texte[i:i + batch_size]
        
        # Den Payload exakt so bauen, wie die Google-API ihn erwartet
        payload = {
            "requests": [
                {"model": "models/text-embedding-004", "content": {"parts": [{"text": t}]}} for t in batch
            ]
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code != 200:
            print(f"❌ API-Fehler: {response.text}")
            return
            
        data = response.json()
        for emb in data['embeddings']:
            alle_embeddings.append(emb['values'])
            
        time.sleep(1) # Kurze Pause, um die API zu schonen

    df_kunden['embedding'] = alle_embeddings

    # 3. In DuckDB speichern
    print("Speichere Embeddings in DuckDB...")
    con.execute("DROP TABLE IF EXISTS staging.kunden_embeddings")
    
    # Wir legen die Tabelle mit dem speziellen Vektor-Datentyp an (768 Dimensionen)
    con.execute("""
        CREATE TABLE staging.kunden_embeddings (
            praxis VARCHAR,
            quell_zeile INTEGER,
            quell_text VARCHAR,
            embedding FLOAT[768]
        )
    """)
    con.execute("INSERT INTO staging.kunden_embeddings SELECT praxis, quell_zeile, quell_text, embedding FROM df_kunden")

    # 4. Den Vector-Index anlegen
    print("Erstelle HNSW Vector-Index für die DuckDB VSS...")
    con.execute("INSTALL vss;")
    con.execute("LOAD vss;")
    con.execute("DROP INDEX IF EXISTS idx_kunden_emb;")
    
    # HNSW Index optimiert die Ähnlichkeitssuche
    con.execute("""
        CREATE INDEX idx_kunden_emb 
        ON staging.kunden_embeddings 
        USING HNSW (embedding)
    """)

    # 5. Kurze Erfolgskontrolle
    count = con.execute("SELECT COUNT(*) FROM staging.kunden_embeddings").fetchone()[0]
    print(f"\n✅ MEILENSTEIN W8 KOMPLETT! Es wurden {count} Vektoren erfolgreich indiziert.")

if __name__ == "__main__":
    main()