import duckdb
import networkx as nx
import pandas as pd

def main():
    print("Starte Cluster-Bildung (Transitive Hülle)...")
    
    # 1. Verbindung zur Datenbank
    con = duckdb.connect("verbund.duckdb")
    
    # 2. Alle echten Dubletten-Paare aus dem LLM-Matching laden
    # Auch die 0.0 Distanz-Treffer sollten hier drin sein, wenn du sie vorher per SQL eingefügt hast
    matches = con.execute("""
        SELECT praxis_a, id_a, praxis_b, id_b 
        FROM staging.match_entscheidung 
        WHERE is_duplicate = TRUE
    """).df()
    
    if matches.empty:
        print("Keine Dubletten gefunden. Beende Skript.")
        return

    # 3. Graph erstellen
    G = nx.Graph()
    
    # Knoten und Kanten hinzufügen
    for _, row in matches.iterrows():
        # Wir kombinieren Praxis-ID und Quell-ID zu einem eindeutigen String
        knoten_a = f"{row['praxis_a']}_{row['id_a']}"
        knoten_b = f"{row['praxis_b']}_{row['id_b']}"
        G.add_edge(knoten_a, knoten_b)
        
    # 4. Zusammenhängende Komponenten (Cluster) finden
    cluster_mapping = []
    cluster_id_counter = 1
    
    print("Berechne verbundene Komponenten...")
    for component in nx.connected_components(G):
        for knoten in component:
            # Den String wieder in Praxis-ID und Quell-ID aufsplitten
            praxis_id, quell_id = knoten.split('_', 1)
            
            cluster_mapping.append({
                'praxis_id': int(praxis_id),
                'quell_id': quell_id,
                'cluster_id': cluster_id_counter
            })
        cluster_id_counter += 1
        
    df_clusters = pd.DataFrame(cluster_mapping)
    
    # 5. Mapping in DuckDB speichern
    print("Speichere Cluster-Mapping in staging.cluster_mapping...")
    con.execute("DROP TABLE IF EXISTS staging.cluster_mapping")
    con.execute("""
        CREATE TABLE staging.cluster_mapping (
            praxis_id INTEGER,
            quell_id VARCHAR,
            cluster_id INTEGER
        )
    """)
    con.execute("INSERT INTO staging.cluster_mapping SELECT * FROM df_clusters")
    
    print(f"✅ {len(df_clusters)} Datensätze wurden erfolgreich in {cluster_id_counter - 1} Clustern zusammengefasst.")
    con.close()

if __name__ == "__main__":
    main()



import duckdb

def main():
    print("Starte konsolidierte Beladung des Zielschemas...")
    con = duckdb.connect("verbund.duckdb")

    # 1. Zielschema einlesen
    with open('zielschema.sql', 'r', encoding='utf-8') as f:
        schema_sql = f.read()
        
    # Stammdaten abschneiden
    schema_sql = schema_sql.split('-- Stammdaten')[0]
    schema_sql = schema_sql.replace('SERIAL PRIMARY KEY', 'INTEGER PRIMARY KEY')

    con.execute(schema_sql)
    con.execute("ALTER TABLE verbund_kunde ADD COLUMN cluster_id INTEGER;")

    print("Lade alle 4 Praxen...")
    con.execute("""
        INSERT INTO verbund_praxis (praxis_id, kurzname, name, plz, ort) VALUES
        (1, 'JUCK', 'Tierarztpraxis Canini', '35500', 'Juckstadt'),
        (2, 'WALD', 'Kleintierpraxis Waldrand', '35466', 'Rabenau'),
        (3, 'SCHM', 'Tierarztzentrum Schmidt', '35578', 'Wetzlar'),
        (4, 'BERG', 'Tierklinik Bergblick', '35510', 'Bergblick-Siedlung');
    """)

    print("Vergebe Cluster-IDs...")
    # Leere Geister-Zeilen ignorieren
    con.execute("""
        CREATE OR REPLACE TABLE staging.alle_kunden_cluster AS
        SELECT 
            k.*,
            COALESCE(c.cluster_id, 10000 + ROW_NUMBER() OVER()) AS cluster_id
        FROM transform.norm_kunde k
        LEFT JOIN staging.cluster_mapping c
          ON k.praxis_id = c.praxis_id AND k.quell_id = c.quell_id
        WHERE k.nachname IS NOT NULL OR k.quell_id IS NOT NULL
    """)

    print("Erstelle Golden Records (Kunden)...")
    # 4. Golden Records (mit COALESCE für NOT NULL Spalten)
    con.execute("CREATE SEQUENCE IF NOT EXISTS seq_vkunde;")
    con.execute("""
        INSERT INTO verbund_kunde (
            kunde_id, praxis_id, quell_id, anrede, vorname, nachname, 
            strasse, plz, ort, telefon_e164, email, erfasst_am, cluster_id
        )
        SELECT 
            nextval('seq_vkunde'),
            COALESCE(MAX(praxis_id), 1),
            COALESCE(MAX(quell_id), 'GEN-' || CAST(cluster_id AS VARCHAR)), 
            MAX(anrede),
            MAX(vorname),
            COALESCE(MAX(nachname), 'Unbekannt'), -- FIX: Falls Name fehlt
            MAX(strasse),
            MAX(plz),
            MAX(ort),
            MAX(telefon),
            MAX(email),
            TRY_CAST(MAX(erfasst_am) AS DATE),
            cluster_id
        FROM staging.alle_kunden_cluster
        GROUP BY cluster_id
    """)

    print("Mappe Behandlungen auf den Golden Record...")
    # 5. Behandlungen (mit COALESCE für NOT NULL Datum)
    con.execute("CREATE SEQUENCE IF NOT EXISTS seq_vbehandlung;")
    con.execute("""
        INSERT INTO verbund_behandlung (
            behandlung_id, praxis_id, quell_id, kunde_id, datum, tier_name, tierart, diagnose, betrag_eur
        )
        SELECT 
            nextval('seq_vbehandlung'),
            COALESCE(b.praxis_id, 1),
            COALESCE(b.quell_id, 'B-GEN-' || CAST(ROW_NUMBER() OVER() AS VARCHAR)),
            vk.kunde_id, 
            COALESCE(TRY_CAST(b.datum AS DATE), '1999-01-01'::DATE), -- FIX: Falls Datum fehlt
            b.tier_name,
            b.tierart,
            b.diagnose,
            b.betrag_eur
        FROM transform.norm_behandlung b
        JOIN staging.alle_kunden_cluster akc
          ON b.praxis_id = akc.praxis_id AND b.kunden_referenz = akc.quell_id
        JOIN verbund_kunde vk
          ON akc.cluster_id = vk.cluster_id
    """)

    k_count = con.execute("SELECT COUNT(*) FROM verbund_kunde").fetchone()[0]
    b_count = con.execute("SELECT COUNT(*) FROM verbund_behandlung").fetchone()[0]
    
    print("-" * 50)
    print(f"✅ {k_count} Golden Records (Kunden) erfolgreich erstellt.")
    print(f"✅ {b_count} Behandlungen nahtlos zugeordnet.")
    
    con.close()

if __name__ == "__main__":
    main()


import duckdb
import pandas as pd
from itertools import combinations

def get_pairs(df, cluster_col, praxis_col, id_col):
    pairs = set()
    for _, group in df.groupby(cluster_col):
        if len(group) > 1:
            records = set(group[praxis_col].astype(str) + "_" + group[id_col].astype(str))
            for pair in combinations(sorted(records), 2):
                pairs.add(pair)
    return pairs

def main():
    print("Starte F1-Score Evaluierung...")
    
    # 1. Goldstandard laden
    df_gold = pd.read_csv('gold_cluster.csv')
    mapping = {'JUCK': '1', 'WALD': '2', 'SCHM': '3', 'BERG': '4'}
    df_gold['praxis_id'] = df_gold['praxis'].map(mapping)
    
    # 2. Eigene Ergebnisse laden
    con = duckdb.connect("verbund.duckdb")
    df_pred = con.execute("""
        SELECT praxis_id, CAST(quell_id AS VARCHAR) as quell_id, cluster_id 
        FROM staging.alle_kunden_cluster
        WHERE quell_id NOT LIKE 'GEN-%'
    """).df()
    con.close()
    
    # 3. Paare generieren
    gold_pairs = get_pairs(df_gold, 'cluster_id', 'praxis_id', 'quell_id')
    pred_pairs = get_pairs(df_pred, 'cluster_id', 'praxis_id', 'quell_id')
    
    # 4. Metriken berechnen
    true_positives = len(gold_pairs.intersection(pred_pairs))
    false_positives = len(pred_pairs - gold_pairs)
    false_negatives = len(gold_pairs - pred_pairs)
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    # 5. Protokoll-Ausgabe (DEIN GEWÜNSCHTES FORMAT)
    print("\n" + "="*50)
    print(" ERGEBNISSE FÜR W11 DOKUMENTATION")
    print("="*50)
    print(f"Gefundene Dubletten-Paare (LLM) : {len(pred_pairs)}")
    print(f"Echte Dubletten-Paare (Gold)    : {len(gold_pairs)}")
    print("-" * 50)
    print(f"Korrekt gefunden (True Positives)    : {true_positives}")
    print(f"Falsch verknüpft (False Positives)   : {false_positives}")
    print(f"Übersehen / Nicht erkannt (False Neg.): {false_negatives}")
    print("-" * 50)
    print(f"🎯 Precision (Genauigkeit) : {precision:.2%}")
    print(f"🎯 Recall (Trefferquote)   : {recall:.2%}")
    print(f"🏆 F1-Score               : {f1_score:.2%}")
    print("=" * 50)

if __name__ == "__main__":
    main()
