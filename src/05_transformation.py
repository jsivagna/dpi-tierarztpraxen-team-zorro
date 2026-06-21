import duckdb
import pandas as pd

def transformiere_tabelle(con, tabellen_name):
    print(f"Transformiere Tabelle: {tabellen_name} ...")
    
    # 1. Daten in ein Pandas DF laden
    df = con.execute(f"SELECT * FROM staging.{tabellen_name}").df()
    
    # 2. Definition aus DATA_DICTIONARY
    exakte_preis_spalten = ['kosten_euro', 'total_eur', 'betrag', 'brutto']
    exakte_datum_spalten = ['angelegt_am', 'created_at', 'erfasst', 'datum', 'treatment_date']
    
    # 3. Komma-Bereinigung (Zahlen / Währungen)
    for col in exakte_preis_spalten:
        if col in df.columns:
            if df[col].dtype == 'object': 
                df[col] = df[col].astype(str).str.replace(',', '.')
                df[col] = df[col].str.replace(r'[^\d.]', '', regex=True)
                df[col] = pd.to_numeric(df[col], errors='coerce')
                print(f"   Spalte '{col}' wurde zu Float (mit Punkt) transformiert.")

    # 4. Datums-Bereinigung (YYYY-MM-DD)
    for col in exakte_datum_spalten:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
            df[col] = df[col].dt.strftime('%Y-%m-%d')
            print(f"   Spalte '{col}' wurde in ISO-Format transformiert.")

    # 5. Bereinigte Daten als neue Tabelle zurück in DuckDB schreiben
    ziel_tabelle = f"{tabellen_name}_clean"
    con.execute(f"DROP TABLE IF EXISTS staging.{ziel_tabelle}")
    con.execute(f"CREATE TABLE staging.{ziel_tabelle} AS SELECT * FROM df")

def erstelle_norm_tabellen(con):
    con.execute("CREATE SCHEMA IF NOT EXISTS transform;")
    
    # ---------------------------------------------------------
    # 1. NORM_KUNDE erstellen
    # ---------------------------------------------------------
    print("   -> Erstelle transform.norm_kunde...")
    con.execute("DROP TABLE IF EXISTS transform.norm_kunde;")
    
    query_kunde = """
    CREATE TABLE transform.norm_kunde AS 
    
    -- Juckstadt (Praxis 1)
    SELECT 1 AS praxis_id, CAST(kunden_nr AS VARCHAR) AS quell_id, 
           anrede, vorname, nachname, strasse, CAST(plz AS VARCHAR) AS plz, 
           ort, telefon, email, angelegt_am AS erfasst_am
    FROM staging.juck_kunden_clean
    
    UNION ALL
    
    -- Waldrand (Praxis 2)
    SELECT 2 AS praxis_id, CAST(customer_id AS VARCHAR) AS quell_id, 
           NULL AS anrede, first_name AS vorname, last_name AS nachname, 
           street AS strasse, CAST(zip_code AS VARCHAR) AS plz, 
           city AS ort, phone AS telefon, email_address AS email, 
           created_at AS erfasst_am
    FROM staging.wald_kunden_clean
    
    UNION ALL
    
    -- Schmidt (Praxis 3)
    SELECT 3 AS praxis_id, NULL AS quell_id, 
           anrede, vorname, nachname, strasse, CAST(plz AS VARCHAR) AS plz, 
           ort, tel AS telefon, email, erfasst AS erfasst_am
    FROM staging.schm_kunden_clean
    
    UNION ALL
    
    -- Bergblick (Praxis 4) - Nutzt quell_zeile als ID
    SELECT 4 AS praxis_id, CAST(quell_zeile AS VARCHAR) AS quell_id, 
           anrede, NULL AS vorname, name AS nachname, strasse, 
           CAST(plz AS VARCHAR) AS plz, ort, telefon, email, 
           NULL AS erfasst_am
    FROM staging.berg_patienten_clean
    """
    con.execute(query_kunde)

    # ---------------------------------------------------------
    # 2. NORM_BEHANDLUNG erstellen
    # ---------------------------------------------------------
    print("   -> Erstelle transform.norm_behandlung...")
    con.execute("DROP TABLE IF EXISTS transform.norm_behandlung;")
    
    query_behandlung = """
    CREATE TABLE transform.norm_behandlung AS 
    
    -- Juckstadt (Praxis 1)
    SELECT 1 AS praxis_id, CAST(beh_nr AS VARCHAR) AS quell_id, 
           kunde_nachname AS kunden_referenz, datum, patient_name AS tier_name, 
           NULL AS tierart, diagnose, kosten_euro AS betrag_eur
    FROM staging.juck_behandlungen_clean
    
    UNION ALL
    
    -- Waldrand (Praxis 2)
    SELECT 2 AS praxis_id, CAST(treatment_id AS VARCHAR) AS quell_id, 
           CAST(customer_id AS VARCHAR) AS kunden_referenz, treatment_date AS datum, 
           animal_name AS tier_name, species AS tierart, diagnosis AS diagnose, 
           total_eur AS betrag_eur
    FROM staging.wald_behandlungen_clean
    
    UNION ALL
    
    -- Schmidt (Praxis 3) - Entpackt das JSON-Objekt "tier"
SELECT 3 AS praxis_id, CAST(id AS VARCHAR) AS quell_id, 
           kunde AS kunden_referenz, datum, 
           regexp_extract(CAST(tier AS VARCHAR), '''name'':\s*''?([^''},]+)', 1) AS tier_name, 
           regexp_extract(CAST(tier AS VARCHAR), '''art'':\s*''?([^''},]+)', 1) AS tierart, 
           leistung AS diagnose, betrag AS betrag_eur
    FROM staging.schm_behandlungen_clean
    
    UNION ALL
    
    -- Bergblick (Praxis 4) - Fehlende Attribute mit NULL aufgefüllt
    SELECT 4 AS praxis_id, CAST(quell_zeile AS VARCHAR) AS quell_id, 
           CAST(NULL AS VARCHAR) AS kunden_referenz, 
           CAST(NULL AS VARCHAR) AS datum, 
           NULL AS tier_name, NULL AS tierart, diagnose, 
           CAST(NULL AS FLOAT) AS betrag_eur
    FROM staging.berg_behandlungen_clean
    """
    con.execute(query_behandlung)


def main():
    print("Daten-Transformation laut Data Dictionary...\n")
    print("-" * 65)
    
    con = duckdb.connect("verbund.duckdb")
    
    try:
        tabellen_zu_pruefen = [
            'juck_kunden', 'juck_behandlungen', 
            'wald_kunden', 'wald_behandlungen', 
            'schm_kunden', 'schm_behandlungen',
            'berg_patienten', 'berg_behandlungen'
        ]
        
        for tab in tabellen_zu_pruefen:
            check = con.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='staging' AND table_name='{tab}'").fetchone()[0]
            if check > 0:
                transformiere_tabelle(con, tab)
            else:
                print(f"! Tabelle {tab} nicht gefunden, wird übersprungen.")
                

        erstelle_norm_tabellen(con)
        
        print("\n Success: Alle Tabellen wurden bereinigt und erfolgreich in 'transform.norm_kunde' und 'transform.norm_behandlung' vereint")
        
    finally:
        con.close()

if __name__ == "__main__":
    main()
