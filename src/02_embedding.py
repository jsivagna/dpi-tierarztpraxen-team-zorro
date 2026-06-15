"""
VORAUSSETZUNGEN (Linux / Colab Terminal-Befehle):
Bevor dieses Skript ausgeführt wird, muss Ollama lokal laufen und das Modell geladen sein:

1. Entpack-Tool installieren:  apt-get install -y zstd
2. Ollama installieren:        curl -fsSL https://ollama.com/install.sh | sh
3. Server starten:             nohup ollama serve > ollama.log 2>&1 &
4. Modell laden:               ollama pull nomic-embed-text
"""

import duckdb
import pandas as pd
import requests

def lade_kunden(con, praxis_name, tabellen_name):
   # Holt alle Zeilen einer Tabelle und macht einen langen Text-String daraus
    df = con.execute(f"SELECT * FROM staging.{tabellen_name}").df()
    kunden = []
    for index, row in df.iterrows():
        row_dict = row.dropna().to_dict()
        quell_zeile = row_dict.pop('quell_zeile', index)
        text_string = " | ".join([f"{k}: {v}" for k, v in row_dict.items()])
        kunden.append({
            'praxis': praxis_name,
            'quell_zeile': int(quell_zeile),
            'quell_text': text_string
        })
    return kunden

def main():
    print("Starte KI-Embedding-Prozess (Ollama)")
    con = duckdb.connect("verbund.duckdb")

    print("Sammle Kundendaten aus allen Praxen...")
    alle_kunden = []
    alle_kunden.extend(lade_kunden(con, 'Juckstadt', 'juck_kunden'))
    alle_kunden.extend(lade_kunden(con, 'Waldrand', 'wald_kunden'))
    alle_kunden.extend(lade_kunden(con, 'Schmidt', 'schm_kunden'))
    alle_kunden.extend(lade_kunden(con, 'Bergblick', 'berg_patienten'))
    
    df_kunden = pd.DataFrame(alle_kunden)
    print(f"Insgesamt {len(df_kunden)} Kunden gefunden.")

    print("Berechne Embeddings mit 'nomic-embed-text'...")
    alle_embeddings = []
    
    for text in df_kunden['quell_text'].tolist():
        # Direkter REST-Aufruf an den lokalen Ollama-Server
        response = requests.post(
            "http://localhost:11434/api/embeddings",
            json={
                "model": "nomic-embed-text",
                "prompt": text
            }
        )
        
        if response.status_code == 200:
            alle_embeddings.append(response.json()['embedding'])
        else:
            print(f" Fehler bei Ollama: {response.text}")
            return

    df_kunden['embedding'] = alle_embeddings

    print("Speichere Embeddings in DuckDB...")
    con.execute("DROP TABLE IF EXISTS staging.kunden_embeddings")
    
    con.execute("""
        CREATE TABLE staging.kunden_embeddings (
            praxis VARCHAR,
            quell_zeile INTEGER,
            quell_text VARCHAR,
            embedding FLOAT[768]
        )
    """)
    con.execute("INSERT INTO staging.kunden_embeddings SELECT praxis, quell_zeile, quell_text, embedding FROM df_kunden")

    print("Erstelle HNSW Vector-Index für die DuckDB VSS...")
    con.execute("INSTALL vss;")
    con.execute("LOAD vss;")

    con.execute("SET hnsw_enable_experimental_persistence = true;")
    con.execute("DROP INDEX IF EXISTS idx_kunden_emb;")
    
    con.execute("""
        CREATE INDEX idx_kunden_emb 
        ON staging.kunden_embeddings 
        USING HNSW (embedding)
    """)

    count = con.execute("SELECT COUNT(*) FROM staging.kunden_embeddings").fetchone()[0]
    print(f"\n Success; Es wurden erfolgreich {count} Vektoren indiziert.")

if __name__ == "__main__":
    main()
