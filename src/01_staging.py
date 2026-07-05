import duckdb
import pandas as pd
import xml.etree.ElementTree as ET

def init_zielschema(con):
    print("Initialisiere Zielschema laut Vorgabe des Profs ...")
    
    con.execute("DROP TABLE IF EXISTS verbund_behandlung CASCADE;")
    con.execute("DROP TABLE IF EXISTS verbund_kunde CASCADE;")
    con.execute("DROP TABLE IF EXISTS verbund_praxis CASCADE;")

    con.execute("""
        CREATE TABLE verbund_praxis (
            praxis_id       INTEGER PRIMARY KEY,
            kurzname        VARCHAR(20) NOT NULL UNIQUE,
            name            VARCHAR(100) NOT NULL,
            plz             VARCHAR(10),
            ort             VARCHAR(50)
        );

        CREATE TABLE verbund_kunde (
            kunde_id        INTEGER PRIMARY KEY,
            praxis_id       INTEGER NOT NULL REFERENCES verbund_praxis(praxis_id),
            quell_id        VARCHAR(30) NOT NULL,
            anrede          VARCHAR(20),
            vorname         VARCHAR(50),
            nachname        VARCHAR(50) NOT NULL,
            strasse         VARCHAR(100),
            plz             VARCHAR(10),
            ort             VARCHAR(50),
            telefon_e164    VARCHAR(20),
            email           VARCHAR(100),
            erfasst_am      DATE,
            cluster_id      VARCHAR(50),  -- NEU: Vom Prof vorgegeben!
            UNIQUE (praxis_id, quell_id)
        );

        CREATE TABLE verbund_behandlung (
            behandlung_id   INTEGER PRIMARY KEY,
            praxis_id       INTEGER NOT NULL REFERENCES verbund_praxis(praxis_id),
            quell_id        VARCHAR(30) NOT NULL,
            kunde_id        INTEGER REFERENCES verbund_kunde(kunde_id),
            datum           DATE NOT NULL,
            tier_name       VARCHAR(50),
            tierart         VARCHAR(20),
            diagnose        TEXT,
            betrag_eur      NUMERIC(10,2),
            UNIQUE (praxis_id, quell_id)
        );
    """)

    con.execute("""
        INSERT INTO verbund_praxis (praxis_id, kurzname, name, plz, ort) VALUES
          (1, 'JUCK', 'Tierarztpraxis Canini',   '35500', 'Juckstadt'),
          (2, 'WALD', 'Kleintierpraxis Waldrand','35466', 'Rabenau'),
          (3, 'SCHM', 'Tierarztzentrum Schmidt', '35578', 'Wetzlar'),
          (4, 'BERG', 'Tierklinik Bergblick',    '35510', 'Waldrand');
    """)

def lade_staging_daten(con):
    print("Starte Staging-Prozess für Juckstadt, Waldrand & Schmidt (CSV/JSON) ...")
    con.execute("CREATE SCHEMA IF NOT EXISTS staging;")

    # 1. Praxis Juckstadt
    print(" -> Lade Daten von Juckstadt...")
    con.execute("CREATE OR REPLACE TABLE staging.juck_kunden AS SELECT row_number() OVER () as quell_zeile, * FROM read_csv_auto('data/praxis_juckstadt_kunden.csv', sep=';')")
    con.execute("CREATE OR REPLACE TABLE staging.juck_behandlungen AS SELECT row_number() OVER () as quell_zeile, * FROM read_csv_auto('data/praxis_juckstadt_behandlungen.csv', sep=';')")

    # 2. Praxis Waldrand
    print(" -> Lade Daten von Waldrand...")
    con.execute("CREATE OR REPLACE TABLE staging.wald_kunden AS SELECT row_number() OVER () as quell_zeile, * FROM read_csv_auto('data/praxis_waldrand_kunden.csv')")
    con.execute("CREATE OR REPLACE TABLE staging.wald_behandlungen AS SELECT row_number() OVER () as quell_zeile, * FROM read_csv_auto('data/praxis_waldrand_behandlungen.csv')")

    # 3. Praxis Schmidt
    print(" -> Lade Daten von Schmidt...")
    con.execute("CREATE OR REPLACE TABLE staging.schm_kunden AS SELECT row_number() OVER () as quell_zeile, * FROM read_csv_auto('data/praxis_schmidt_kunden.csv', sep='|')")
    con.execute("""
        CREATE OR REPLACE TABLE staging.schm_behandlungen AS 
        SELECT 
            row_number() OVER () as quell_zeile,
            id,
            datum,
            kunde,
            tier->>'name' AS tier_name,
            tier->>'art' AS tier_art,
            leistung,
            betrag
        FROM read_json_auto('data/praxis_schmidt_behandlungen.json')
    """)
def lade_bergblick_xml(con):
    print(" -> Lade Daten von Bergblick...")
    tree = ET.parse('data/praxis_bergblick_export.xml')
    root = tree.getroot()
    # Namespace für das XML
    ns = {'ns': 'http://vetkliniken-hessen.de/schema/v2'}

    patienten_liste = []
    behandlungen_liste = []

    # Patienten parsen (tiefe Struktur extrahieren)
    for patient in root.findall('.//ns:patient', ns):
        halter = patient.find('ns:halter', ns)
        kontakt = halter.find('ns:kontakt', ns) if halter is not None else None
        adresse = halter.find('ns:adresse', ns) if halter is not None else None
        tier = patient.find('ns:tier', ns)

        daten = {
            'quell_id': patient.get('id'),
            'erfasst': halter.get('erfasst') if halter is not None else None,
            'anrede': halter.find('ns:anrede', ns).text if halter is not None and halter.find('ns:anrede', ns) is not None else None,
            'name': halter.find('ns:name', ns).text if halter is not None and halter.find('ns:name', ns) is not None else None,
            'telefon': kontakt.find('ns:telefon', ns).text if kontakt is not None and kontakt.find('ns:telefon', ns) is not None else None,
            'email': kontakt.find('ns:email', ns).text if kontakt is not None and kontakt.find('ns:email', ns) is not None else None,
            'strasse': adresse.find('ns:strasse', ns).text if adresse is not None and adresse.find('ns:strasse', ns) is not None else None,
            'plz': adresse.find('ns:plz', ns).text if adresse is not None and adresse.find('ns:plz', ns) is not None else None,
            'ort': adresse.find('ns:ort', ns).text if adresse is not None and adresse.find('ns:ort', ns) is not None else None

        }
        patienten_liste.append(daten)

    # Behandlungen parsen
    for beh in root.findall('.//ns:behandlung', ns):
        summe = beh.find('ns:summe', ns)
        daten = {
            'patient_id': beh.get('patientId'),
            'datum': beh.get('datum'),
            'diagnose': beh.find('ns:diagnose', ns).text if beh.find('ns:diagnose', ns) is not None else None,
            'tier_name': tier.find('ns:name', ns).text if tier is not None and tier.find('ns:name', ns) is not None else None,
            'tier_art': tier.find('ns:art', ns).text if tier is not None and tier.find('ns:art', ns) is not None else None,
            'betrag_netto': summe.get('netto') if summe is not None else None
        }
        behandlungen_liste.append(daten)

    df_pat = pd.DataFrame(patienten_liste)
    df_beh = pd.DataFrame(behandlungen_liste)

    con.register('df_pat_view', df_pat)
    con.register('df_beh_view', df_beh)

    # Erstelle Staging-Tabellen für Bergblick
    con.execute("CREATE OR REPLACE TABLE staging.berg_patienten AS SELECT row_number() OVER () as quell_zeile, * FROM df_pat_view")
    con.execute("CREATE OR REPLACE TABLE staging.berg_behandlungen AS SELECT row_number() OVER () as quell_zeile, * FROM df_beh_view")


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

def zeige_tabellen_inhalte(con):
    print("\n" + "="*60)
    print(" ÜBERPRÜFUNG: ZIELSCHEMA & STAGING-DATEN")
    print("="*60)

    # 1. Zeige die 3 Tabellen aus dem Zielschema
    print("\n--- ZIELSCHEMA: verbund_praxis ---")
    df_praxis = con.execute("SELECT * FROM verbund_praxis").df()
    print(df_praxis)

    print("\n--- ZIELSCHEMA: verbund_kunde (Struktur - noch leer) ---")
    df_kunde = con.execute("SELECT * FROM verbund_kunde LIMIT 3").df()
    print("Spalten:", list(df_kunde.columns), "| Zeilen (aktuell):", len(df_kunde))

    print("\n--- ZIELSCHEMA: verbund_behandlung (Struktur - noch leer) ---")
    df_beh = con.execute("SELECT * FROM verbund_behandlung LIMIT 3").df()
    print("Spalten:", list(df_beh.columns), "| Zeilen (aktuell):", len(df_beh))

    print("\n" + "-"*60)

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)

    # 2. Zeige alle 8 Staging Tabellen
    staging_tabellen = [
        'juck_kunden', 
        'wald_kunden', 
        'schm_kunden',
        'berg_patienten',
        'juck_behandlungen',
        'wald_behandlungen',
         'schm_behandlungen',
        'berg_behandlungen'
    ]

    for tab in staging_tabellen:
        print(f"\n--- ROHDATEN: staging.{tab} ---")
        try:
            df = con.execute(f"SELECT * FROM staging.{tab}").df()
            print(df)
        except Exception as e:
            print(f"Fehler beim Lesen von {tab}: {e}")

def main():
    # Verbindung zur Datenbank herstellen
    con = duckdb.connect("verbund.duckdb")

    # Schritte ausführen
    init_zielschema(con)
    lade_staging_daten(con)
    lade_bergblick_xml(con)
    zeige_statistik(con)
    
    # Ergebnisse zur Prüfung anzeigen
    zeige_tabellen_inhalte(con)

    con.close()
    print("\n Staging abgeschlossen.")

if __name__ == "__main__":
    main()
