import duckdb
import pandas as pd
import xml.etree.ElementTree as ET

def lade_csv_json(con):
    print("Starte Staging-Prozess: CSV & JSON ...")
    
    # Schema anlegen
    con.execute("CREATE SCHEMA IF NOT EXISTS staging;")

    # 1. Praxis Juckstadt (CSV)
    print("Lade Daten von Juckstadt...")
    con.execute("""
        CREATE OR REPLACE TABLE staging.juck_kunden AS 
        SELECT row_number() OVER () as quell_zeile, * FROM read_csv_auto('data/praxis_juckstadt_kunden.csv', sep=';')
    """)
    con.execute("""
        CREATE OR REPLACE TABLE staging.juck_behandlungen AS 
        SELECT row_number() OVER () as quell_zeile, * FROM read_csv_auto('data/praxis_juckstadt_behandlungen.csv', sep=';')
    """)

    # 2. Praxis Waldrand (CSV)
    print("Lade Daten von Waldrand...")
    con.execute("""
        CREATE OR REPLACE TABLE staging.wald_kunden AS 
        SELECT row_number() OVER () as quell_zeile, * FROM read_csv_auto('data/praxis_waldrand_kunden.csv')
    """)
    con.execute("""
        CREATE OR REPLACE TABLE staging.wald_behandlungen AS 
        SELECT row_number() OVER () as quell_zeile, * FROM read_csv_auto('data/praxis_waldrand_behandlungen.csv')
    """)

    # 3. Praxis Schmidt (CSV und JSON)
    print("Lade Daten von Schmidt...")
    con.execute("""
        CREATE OR REPLACE TABLE staging.schm_kunden AS 
        SELECT row_number() OVER () as quell_zeile, * FROM read_csv_auto('data/praxis_schmidt_kunden.csv', sep='|')
    """)
    con.execute("""
        CREATE OR REPLACE TABLE staging.schm_behandlungen AS 
        SELECT row_number() OVER () as quell_zeile, * FROM read_json_auto('data/praxis_schmidt_behandlungen.json')
    """)

def lade_bergblick_xml(con):
    print("Starte Staging-Prozess: XML...")
    
    # XML parsen 
    tree = ET.parse('data/praxis_bergblick_export.xml')
    root = tree.getroot()
    
    # Listen für Patienten und Behandlunge
    patienten_liste = []
    behandlungen_liste = []
    
    zeile_pat = 1
    zeile_beh = 1
    
    # Iteration
    for element in root.iter():
        tag_name = element.tag.split('}')[-1] 
        
        # Patienten extrahieren
        if tag_name == 'patient':
            daten = {'quell_zeile': zeile_pat}
            for child in element.iter():
                child_tag = child.tag.split('}')[-1]
                if child.text and child.text.strip():
                    daten[child_tag] = child.text.strip()
            patienten_liste.append(daten)
            zeile_pat += 1
            
        # Behandlungen extrahieren
        elif tag_name == 'behandlung':
            daten = {'quell_zeile': zeile_beh}
            for child in element.iter():
                child_tag = child.tag.split('}')[-1]
                if child.text and child.text.strip():
                    daten[child_tag] = child.text.strip()
            behandlungen_liste.append(daten)
            zeile_beh += 1

    # In Tabellen umwandeln und in DuckDB speichern
    df_pat = pd.DataFrame(patienten_liste)
    df_beh = pd.DataFrame(behandlungen_liste)
    
    con.execute("CREATE OR REPLACE TABLE staging.berg_patienten AS SELECT * FROM df_pat")
    con.execute("CREATE OR REPLACE TABLE staging.berg_behandlungen AS SELECT * FROM df_beh")
    
    print(f" Success: {len(df_pat)} Patienten und {len(df_beh)} Behandlungen aus XML geladen.")

def zeige_statistik(con):
    print("\n Prüfstatistik für Staging-Prozess:")
    print("-" * 30)
    
    tabellen = [
        'juck_kunden', 'juck_behandlungen', 
        'wald_kunden', 'wald_behandlungen', 
        'schm_kunden', 'schm_behandlungen',
        'berg_patienten', 'berg_behandlungen'
    ]
    
    for tab in tabellen:
        count = con.execute(f"SELECT COUNT(*) FROM staging.{tab}").fetchone()[0]
        print(f"{tab.ljust(20)}: {count} Zeilen")

def main():
    # 1. Einmalige Verbindung zur Datenbank herstellen
    con = duckdb.connect("verbund.duckdb")
    
    # 2. Die drei Bausteine nacheinander aufrufen
    lade_csv_json(con)
    lade_bergblick_xml(con)
    zeige_statistik(con)
    
    print("\n Staging und Extraktion abgeschlossen!")

if __name__ == "__main__":
    main()
