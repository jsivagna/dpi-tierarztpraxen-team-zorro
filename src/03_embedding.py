# 0. Entpack-Tool für Colab installieren
!apt-get install -y zstd

# 1. Ollama installieren
!curl -fsSL https://ollama.com/install.sh | sh

# 2. Ollama-Server im Hintergrund starten
!nohup ollama serve > ollama.log 2>&1 &

# 3. Warten, bis Server hochgefahren
!sleep 5

# 4. Modell herunterladen (nomic-embed-text)
!ollama pull nomic-embed-text

# 5. Ollama installieren
!pip install ollama


import duckdb
import pandas as pd
import ollama
import time

def build_text(row):
    """
    Baut den Eingabetext laut Prof-Vorgabe: 
    Frühe Tokens werden stärker gewichtet (Name > Adresse > Kontakt)
    """
    parts = [
        f"{row.get('vorname') or ''} {row.get('nachname') or ''}".strip(),
        row.get('strasse') or '',
        f"{row.get('plz') or ''} {row.get('ort') or ''}".strip(),
        row.get('telefon') or '',
        row.get('email') or ''
    ]
    # Entfernt leere Elemente und verbindet sie mit einem Pipe-Symbol
    return " | ".join(p.strip() for p in parts if p and str(p).strip())

def main():
    print("Starte KI-Embedding-Prozess basierend auf transform.norm_kunde...")
    
    # Verbindung zur bestehenden DuckDB herstellen
    con = duckdb.connect("verbund.duckdb")

    # 1. Daten aus der harmonisierten Tabelle laden
    print("Lade transformierte Kundendaten...")
    df_kunden = con.execute("""
        SELECT praxis_id, quell_id, vorname, nachname, strasse, plz, ort, telefon, email 
        FROM transform.norm_kunde
    """).df()
    
    print(f"Insgesamt {len(df_kunden)} harmonisierte Datensätze gefunden.")

    # 2. Texte für das Embedding-Modell vorbereiten
    print("Strukturiere Texte für optimale KI-Gewichtung (Name zuerst)...")
    df_kunden['quell_text'] = df_kunden.apply(build_text, axis=1)

    # 3. Embeddings über die offizielle Ollama-Bibliothek berechnen
    print("Berechne Embeddings mit 'nomic-embed-text' (lokal über Ollama)...")
    alle_embeddings = []
    
    t0 = time.time()
    for index, row in df_kunden.iterrows():
        try:
            resp = ollama.embeddings(model="nomic-embed-text", prompt=row['quell_text'])
            alle_embeddings.append(resp['embedding'])
        except Exception as e:
            print(f" Fehler bei Ollama in Zeile {index}: {e}")
            con.close()
            return

    df_kunden['embedding'] = alle_embeddings
    dt = time.time() - t0
    print(f" -> {len(alle_embeddings)} Vektoren erfolgreich berechnet ({dt:.1f}s insgesamt).")

    # 4. Speichern im staging-Schema (bereit für die Vektorsuche)
    print("Speichere Vektoren in staging.kunden_embeddings...")
    con.execute("DROP TABLE IF EXISTS staging.kunden_embeddings")
    con.execute("""
        CREATE TABLE staging.kunden_embeddings (
            praxis_id INTEGER,
            quell_id VARCHAR,
            quell_text VARCHAR,
            embedding FLOAT[768]
        )
    """)
    
    con.execute("""
        INSERT INTO staging.kunden_embeddings 
        SELECT praxis_id, quell_id, quell_text, embedding FROM df_kunden
    """)

    # 5. VSS Extension laden und HNSW-Index erstellen (wie vom Prof empfohlen)
    print("Erstelle HNSW Vector-Index mit Kosinus-Metrik...")
    con.execute("INSTALL vss;")
    con.execute("LOAD vss;")
    con.execute("SET hnsw_enable_experimental_persistence = true;")
    
    con.execute("DROP INDEX IF EXISTS idx_kunden_emb;")
    con.execute("""
        CREATE INDEX idx_kunden_emb
        ON staging.kunden_embeddings
        USING HNSW (embedding) WITH (metric = 'cosine');
    """)

    # 6. Modell-Metadaten zur Reproduzierbarkeit festhalten
    con.execute("""
        CREATE SCHEMA IF NOT EXISTS embeddings;
        CREATE OR REPLACE TABLE embeddings.modell_meta (
            modell VARCHAR,
            dim INTEGER,
            erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        INSERT INTO embeddings.modell_meta (modell, dim) VALUES ('nomic-embed-text', 768);
    """)

    count = con.execute("SELECT COUNT(*) FROM staging.kunden_embeddings").fetchone()[0]
    print(f"\n Success: Es wurden erfolgreich {count} Vektoren indiziert und für das Matching vorbereitet.")
    con.close()

if __name__ == "__main__":
    main()

import duckdb
import pandas as pd

# 1. Verbindung herstellen
con = duckdb.connect("verbund.duckdb")

# 2. Pandas Anzeige-Optionen anpassen (damit es übersichtlich bleibt)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 60) # Begrenzt die Textlänge optisch

# 3. Die ersten 5 Zeilen der Embedding-Tabelle abrufen
print("--- Inhalt der Tabelle: staging.kunden_embeddings (Top 5) ---")
df_embeddings = con.execute("SELECT * FROM staging.kunden_embeddings LIMIT 5").df()
print(df_embeddings)

# 4. Beweis: Dimensionen des Vektors prüfen
laenge = con.execute("SELECT array_length(embedding) FROM staging.kunden_embeddings LIMIT 1").fetchone()[0]
print(f"\n✅ Erfolgs-Check: Die Embedding-Vektoren bestehen aus exakt {laenge} Dimensionen (Zahlen).")

con.close()
