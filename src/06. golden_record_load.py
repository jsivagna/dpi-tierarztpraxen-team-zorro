import duckdb
import networkx as nx
import pandas as pd

def main():
    print("Starte Cluster-Bildung (Transitive Hülle)...")
    con = duckdb.connect("verbund.duckdb")

    # 1. Echte Dubletten-Paare aus der aktuellen Tabelle laden
    # a_id und b_id (globale kunde_id)
    matches = con.execute("""
        SELECT a_id, b_id
        FROM embeddings.match_entscheidung
        WHERE is_duplicate = TRUE
        AND confidence >= 0.8  -- Wir nehmen nur die sicheren Matches
    """).df()

    if matches.empty:
        print("Keine Dubletten gefunden. Beende Skript.")
        con.close()
        return

    # 2. Graph erstellen
    G = nx.Graph()

    # Kanten (Verbindungen) direkt mit kunde_id hinzufügen
    for _, row in matches.iterrows():
        G.add_edge(row['a_id'], row['b_id'])

    # 3. Zusammenhängende Komponenten (Cluster) finden
    cluster_mapping = []
    cluster_id_counter = 1

    print("Berechne verbundene Komponenten...")
    for component in nx.connected_components(G):
        for kunde_id in component:
            cluster_mapping.append({
                'kunde_id': int(kunde_id),
                'cluster_id': cluster_id_counter
            })
        cluster_id_counter += 1

    df_clusters = pd.DataFrame(cluster_mapping)

    # 4. Mapping in DuckDB speichern
    print("Speichere Cluster-Mapping in embeddings.cluster_mapping...")
    con.execute("DROP TABLE IF EXISTS embeddings.cluster_mapping")
    con.execute("""
        CREATE TABLE embeddings.cluster_mapping (
            kunde_id BIGINT,
            cluster_id INTEGER
        )
    """)
    con.execute("INSERT INTO embeddings.cluster_mapping SELECT * FROM df_clusters")

    print(f"{len(df_clusters)} Datensätze wurden erfolgreich in {cluster_id_counter - 1} Clustern zusammengefasst.")
    con.close()

if __name__ == "__main__":
    main()


import duckdb

def main():
    print("Starte konsolidierte Beladung des Zielschemas (Golden Records)...")
    con = duckdb.connect("verbund.duckdb")

    # 1. Zielschema einlesen
    try:
        with open('zielschema.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()
            
        schema_sql = schema_sql.replace('SERIAL PRIMARY KEY', 'INTEGER PRIMARY KEY')
        if '-- Stammdaten' in schema_sql:
            schema_sql = schema_sql.split('-- Stammdaten')[0]
            
        con.execute(schema_sql)
    except FileNotFoundError:
        print("FEHLER: 'zielschema.sql' nicht gefunden.")
        return

    # 2. Cluster-ID Spalte sicherstellen
    try:
        con.execute("ALTER TABLE verbund_kunde ADD COLUMN cluster_id INTEGER;")
    except duckdb.CatalogException:
        pass 

    # 3. Praxen laden
    print("Lade alle 4 Praxen...")
    con.execute("DELETE FROM verbund_praxis;") 
    con.execute("""
        INSERT INTO verbund_praxis (praxis_id, kurzname, name, plz, ort) VALUES
        (1, 'JUCK', 'Tierarztpraxis Canini', '35500', 'Juckstadt'),
        (2, 'WALD', 'Kleintierpraxis Waldrand', '35466', 'Rabenau'),
        (3, 'SCHM', 'Tierarztzentrum Schmidt', '35578', 'Wetzlar'),
        (4, 'BERG', 'Tierklinik Bergblick', '35510', 'Bergblick-Siedlung');
    """)

    # 4. Cluster-Zuweisung
    print("Vergebe Cluster-IDs an alle Kunden...")
    con.execute("DROP TABLE IF EXISTS transform.alle_kunden_cluster;")
    con.execute("""
        CREATE TABLE transform.alle_kunden_cluster AS
        SELECT
            k.* EXCLUDE (cluster_id),
            COALESCE(c.cluster_id, 10000 + CAST(ROW_NUMBER() OVER(ORDER BY k.kunde_id) AS INTEGER)) AS cluster_id
        FROM transform.norm_kunde k
        LEFT JOIN embeddings.cluster_mapping c
          ON k.kunde_id = c.kunde_id
        WHERE k.nachname IS NOT NULL OR k.quell_id IS NOT NULL
    """)

    # 5. Golden Records (Synthese) erstellen
    print("Erstelle Golden Records (Konsolidierte Kunden)...")
    con.execute("CREATE SEQUENCE IF NOT EXISTS seq_vkunde;")
    con.execute("DELETE FROM verbund_kunde;")
    
    con.execute("""
        INSERT INTO verbund_kunde (
            kunde_id, praxis_id, quell_id, anrede, vorname, nachname,
            strasse, plz, ort, telefon_e164, email, erfasst_am, cluster_id
        )
        SELECT
            nextval('seq_vkunde'),
            arg_max(praxis_id, kunde_id), 
            arg_max(quell_id, kunde_id),
            MAX(anrede),
            MAX(vorname),
            COALESCE(MAX(nachname), 'Unbekannt'),
            MAX(strasse),
            MAX(plz),
            MAX(ort),
            MAX(telefon_e164), 
            MAX(email),
            TRY_CAST(MAX(erfasst_am) AS DATE),
            cluster_id
        FROM transform.alle_kunden_cluster
        GROUP BY cluster_id
    """)

    # 6. Behandlungen 1:1 laden (Neu: LEFT JOIN)
    print("Mappe Behandlungen auf den neuen Golden Record...")
    con.execute("CREATE SEQUENCE IF NOT EXISTS seq_vbehandlung;")
    con.execute("DELETE FROM verbund_behandlung;")
    
    con.execute("""
        INSERT INTO verbund_behandlung (
            behandlung_id, praxis_id, quell_id, kunde_id, datum, tier_name, tierart, diagnose, betrag_eur
        )
        SELECT
            nextval('seq_vbehandlung'),
            COALESCE(b.praxis_id, 1),
            COALESCE(CAST(b.quell_id AS VARCHAR), 'B-GEN-' || CAST(ROW_NUMBER() OVER() AS VARCHAR)),
            vk.kunde_id, -- Wird NULL, wenn der Join ins Leere läuft
            COALESCE(TRY_CAST(b.datum AS DATE), '1999-01-01'::DATE),
            b.tier_name,
            b.tierart,
            b.diagnose,
            b.betrag_eur
        FROM transform.norm_behandlung b
        -- HIER DIE MAGIE: LEFT JOIN zwingt die Datenbank, alle 600 Behandlungen zu behalten!
        LEFT JOIN transform.alle_kunden_cluster akc
          ON b.praxis_id = akc.praxis_id 
          AND (
               TRIM(CAST(b.kunden_id AS VARCHAR)) = TRIM(CAST(akc.quell_id AS VARCHAR)) 
               OR 
               LOWER(TRIM(CAST(b.kunden_id AS VARCHAR))) = LOWER(TRIM(CAST(akc.nachname AS VARCHAR)))
          )
        LEFT JOIN verbund_kunde vk
          ON akc.cluster_id = vk.cluster_id
        QUALIFY ROW_NUMBER() OVER(PARTITION BY b.praxis_id, b.quell_id ORDER BY vk.kunde_id) = 1
    """)

    k_count = con.execute("SELECT COUNT(*) FROM verbund_kunde").fetchone()[0]
    b_count = con.execute("SELECT COUNT(*) FROM verbund_behandlung").fetchone()[0]

    print("-" * 50)
    print(f"{k_count} Golden Records (Kunden) erfolgreich erstellt.")
    print(f"{b_count} Behandlungen 1:1 im Zielschema gelandet.")
    print("\n--- VORSCHAU: VERBUND KUNDE (Top 5 Golden Records) ---")
    print(con.execute("SELECT * FROM verbund_kunde LIMIT 5").df().to_string())

    print("\n--- VORSCHAU: VERBUND BEHANDLUNG (Top 5 Behandlungen) ---")
    print(con.execute("SELECT * FROM verbund_behandlung LIMIT 5").df().to_string())

    con.close()

if __name__ == "__main__":
    main()


import duckdb
import pandas as pd
from itertools import combinations

def get_pairs(df, cluster_col, praxis_col, id_col):
    """Bereinigt Daten und erstellt eindeutige Paar-Keys innerhalb eines Clusters."""
    df[praxis_col] = df[praxis_col].astype(str).str.strip()
    df[id_col] = df[id_col].astype(str).str.strip()

    pairs = set()
    for _, group in df.groupby(cluster_col):
        if len(group) > 1:
            records = set(group[praxis_col] + "_" + group[id_col])
            for pair in combinations(sorted(records), 2):
                pairs.add(pair)
    return pairs

def main():
    print("--- STARTE EVALUIERUNG GEGEN GOLDSTANDARD ---")

    # 1. Goldstandard laden
    try:
        df_gold = pd.read_csv('gold_cluster.csv')
        df_gold['praxis_id'] = df_gold['praxis'].astype(str).str.strip()
        df_gold['quell_id'] = df_gold['quell_id'].astype(str).str.strip()
    except FileNotFoundError:
        print("FEHLER: 'gold_cluster.csv' nicht gefunden!")
        return

    # 2. Eigene Ergebnisse aus der DuckDB laden
    con = duckdb.connect("verbund.duckdb")
    df_pred = con.execute("""
        SELECT
            CASE
                WHEN praxis_id = 1 THEN 'JUCK'
                WHEN praxis_id = 2 THEN 'WALD'
                WHEN praxis_id = 3 THEN 'SCHM'
                WHEN praxis_id = 4 THEN 'BERG'
            END as praxis_id,
            CAST(quell_id AS VARCHAR) as quell_id,
            cluster_id
        FROM transform.alle_kunden_cluster
        WHERE quell_id IS NOT NULL AND quell_id != 'None'
    """).df()
    con.close()

    # 3. Paare generieren (Wer ist mit wem in einem Cluster?)
    gold_pairs = get_pairs(df_gold, 'cluster_id', 'praxis_id', 'quell_id')
    pred_pairs = get_pairs(df_pred, 'cluster_id', 'praxis_id', 'quell_id')

    # 4. Metriken berechnen
    true_positives = len(gold_pairs.intersection(pred_pairs))
    false_positives = len(pred_pairs - gold_pairs)
    false_negatives = len(gold_pairs - pred_pairs)

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    # 5. Finale Ausgabe
    print("\n" + "=" * 50)
    print(" 📊 ERGEBNISSE FÜR DOKUMENTATION")
    print("=" * 50)
    print(f"Gefundene Dubletten-Paare (Dein LLM) : {len(pred_pairs)}")
    print(f"Echte Dubletten-Paare (Goldstandard) : {len(gold_pairs)}")
    print("-" * 50)
    print(f"✅ Korrekt gefunden (True Positives)      : {true_positives}")
    print(f"❌ Falsch verknüpft (False Positives)     : {false_positives}")
    print(f"⚠️ Übersehen (False Negatives)            : {false_negatives}")
    print("-" * 50)
    print(f"🎯 Precision (Genauigkeit) : {precision:.2%}")
    print(f"🎯 Recall (Trefferquote)   : {recall:.2%}")
    print(f"🏆 F1-Score                : {f1_score:.2%}")
    print("=" * 50)

if __name__ == "__main__":
    main()
