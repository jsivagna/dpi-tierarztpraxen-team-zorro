import duckdb

def main():
    print("Starte Staging-Prozess in Colab...")
    
    # Verbinden mit (oder Erstellen von) der Datenbank im Hauptverzeichnis
    con = duckdb.connect("verbund.duckdb")

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

    print("🚀 Staging erfolgreich abgeschlossen!")

if __name__ == "__main__":
    main()