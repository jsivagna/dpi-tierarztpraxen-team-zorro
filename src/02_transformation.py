import duckdb
import pandas as pd
import re

def normalisiere_telefon(tel):
    if pd.isna(tel) or str(tel).strip() == '':
        return None
    # Alle Leerzeichen, Bindestriche und Schrägstriche entfernen
    tel_clean = re.sub(r'[\s\-\/]', '', str(tel))

    # E.164 Format für Deutschland (+49) erzwingen
    if tel_clean.startswith('0049'):
        return '+49' + tel_clean[4:]
    elif tel_clean.startswith('0'):
        return '+49' + tel_clean[1:]
    return tel_clean 

def transformiere_tabelle(con, tabellen_name):
    print(f"Transformiere Tabelle: {tabellen_name} ...")

    # 1. Daten in ein Pandas DF laden
    df = con.execute(f"SELECT * FROM staging.{tabellen_name}").df()

    # 2. Spalten-Definitionen
    exakte_preis_spalten = ['kosten_euro', 'total_eur', 'betrag', 'brutto']
    exakte_datum_spalten = ['angelegt_am', 'created_at', 'erfasst', 'datum', 'treatment_date']
    telefon_spalten = ['telefon', 'phone', 'tel']
    tierart_spalten = ['species', 'art', 'tier_art']

# 3. Komma-Bereinigung (Zahlen / Währungen) - fixt Schmidt ("15,46 EUR") und Juckstadt ("191,17")
    for col in exakte_preis_spalten:
        if col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace(',', '.')
                df[col] = df[col].str.replace(r'[^\d.]', '', regex=True)
                df[col] = pd.to_numeric(df[col], errors='coerce')
                print(f"   -> Spalte '{col}' wurde zu Float transformiert.")

    # 4. Datums-Bereinigung (fixt die rote Warnung!)
    for col in exakte_datum_spalten:
        if col in df.columns:
            if 'wald' in tabellen_name:
                # Waldrand nutzt amerikanisches Format MM/DD/YYYY
                df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=False)
            elif 'berg' in tabellen_name:
                # Bergblick nutzt bereits YYYY-MM-DD
                df[col] = pd.to_datetime(df[col], errors='coerce')
            else:
                # Juckstadt & Schmidt nutzen deutsches Format DD.MM.YYYY
                df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
                
            df[col] = df[col].dt.strftime('%Y-%m-%d')
            print(f"   -> Spalte '{col}' wurde in ISO-Format transformiert.")

    # 5. Telefon-Bereinigung (E.164 Format)
    for col in telefon_spalten:
        if col in df.columns:
            df[col] = df[col].apply(normalisiere_telefon)
            print(f"   -> Spalte '{col}' wurde in E.164-Format transformiert.")

    # 6. Tierart-Übersetzung (Englisch -> Deutsch)
    tier_mapping = {'cat': 'Katze', 'dog': 'Hund', 'bird': 'Vogel', 'rabbit': 'Kaninchen', 'Cat': 'Katze', 'Dog': 'Hund'}
    for col in tierart_spalten:
        if col in df.columns:
            df[col] = df[col].replace(tier_mapping)
            print(f"   -> Spalte '{col}' wurde ins Deutsche übersetzt.")

    # 7. Bereinigte Daten als neue Tabelle zurück in DuckDB schreiben
    ziel_tabelle = f"{tabellen_name}_clean"
    con.execute(f"DROP TABLE IF EXISTS staging.{ziel_tabelle}")
    con.execute(f"CREATE TABLE staging.{ziel_tabelle} AS SELECT * FROM df")

def erstelle_norm_tabellen(con):
    con.execute("CREATE SCHEMA IF NOT EXISTS transform;")

    # ---------------------------------------------------------
    # 1. NORM_KUNDE (Juckstadt + Waldrand)
    # ---------------------------------------------------------
    print("\n   -> Erstelle transform.norm_kunde (Juckstadt + Waldrand)...")
    con.execute("DROP TABLE IF EXISTS transform.norm_kunde;")

    query_kunde = r"""
    CREATE TABLE transform.norm_kunde AS
    
    -- Juckstadt
    SELECT 
        row_number() OVER () AS kunde_id, 
        1 AS praxis_id, 
        CAST(kunden_nr AS VARCHAR) AS quell_id,
        anrede, 
        vorname, 
        nachname, 
        strasse, 
        CAST(plz AS VARCHAR) AS plz,
        ort, 
        telefon AS telefon_e164, 
        email, 
        CAST(angelegt_am AS DATE) AS erfasst_am,
        NULL::INTEGER AS cluster_id
    FROM staging.juck_kunden_clean

    UNION ALL

    -- Waldrand
    SELECT 
        (SELECT COUNT(*) FROM staging.juck_kunden_clean) + 
        row_number() OVER () AS kunde_id,
        2 AS praxis_id, 
        CAST(customer_id AS VARCHAR) AS quell_id,
        NULL AS anrede, 
        first_name AS vorname, 
        last_name AS nachname, 
        street AS strasse, 
        CAST(zip_code AS VARCHAR) AS plz, 
        city AS ort, 
        phone AS telefon_e164, 
        email_address AS email, 
        CAST(created_at AS DATE) AS erfasst_am,
        NULL::INTEGER AS cluster_id
    FROM staging.wald_kunden_clean

    UNION ALL

    -- Schmidt
    SELECT 
        (SELECT COUNT(*) FROM staging.juck_kunden_clean) + 
        (SELECT COUNT(*) FROM staging.wald_kunden_clean) + 
        row_number() OVER () AS kunde_id,
        3 AS praxis_id, 
        CAST(quell_zeile AS VARCHAR) AS quell_id,
        CASE WHEN anrede = 'Hr.' THEN 'Herr' WHEN anrede = 'Fr.' THEN 'Frau' ELSE anrede END AS anrede,
        vorname, 
        nachname, 
        strasse, CAST(plz AS VARCHAR) AS plz, 
        ort, 
        tel AS telefon_e164, email, 
        CAST(erfasst AS DATE) AS erfasst_am, 
        NULL::INTEGER AS cluster_id
    FROM staging.schm_kunden_clean    

    UNION ALL

    -- Bergblick (Praxis 4)
    SELECT 
        (SELECT COUNT(*) FROM staging.juck_kunden_clean) + 
        (SELECT COUNT(*) FROM staging.wald_kunden_clean) +
        (SELECT COUNT(*) FROM staging.schm_kunden_clean) + 
        row_number() OVER () AS kunde_id,
        4 AS praxis_id, 
        CAST(quell_id AS VARCHAR) AS quell_id,
        anrede, 
        string_split(name, ' ')[1] AS vorname, 
        array_to_string(string_split(name, ' ')[2:], ' ') AS nachname, 
        strasse, 
        CAST(plz AS VARCHAR) AS plz, 
        ort, 
        telefon AS telefon_e164, 
        email, 
        CAST(erfasst AS DATE) AS erfasst_am,
        NULL::INTEGER AS cluster_id
    FROM staging.berg_patienten_clean

    """
    con.execute(query_kunde)

    # ---------------------------------------------------------
    # 2. NORM_BEHANDLUNG (Juckstadt + Waldrand)
    # ---------------------------------------------------------
    print("   -> Erstelle transform.norm_behandlung (Juckstadt + Waldrand)...")
    con.execute("DROP TABLE IF EXISTS transform.norm_behandlung;")

    query_behandlung = r"""
    CREATE TABLE transform.norm_behandlung AS
    
    -- Juckstadt
    SELECT 
        row_number() OVER () AS behandlung_id,
        1 AS praxis_id, 
        CAST(beh_nr AS VARCHAR) AS quell_id,
        kunde_nachname AS kunden_id, 
        CAST(datum AS DATE) AS datum, 
        patient_name AS tier_name,
        NULL AS tierart, 
        diagnose, 
        CAST(kosten_euro AS NUMERIC(10,2)) AS betrag_eur
    FROM staging.juck_behandlungen_clean

    UNION ALL

    -- Waldrand
    SELECT 
        (SELECT COUNT(*) FROM staging.juck_behandlungen_clean) + row_number() OVER () AS behandlung_id,
        2 AS praxis_id, 
        CAST(treatment_id AS VARCHAR) AS quell_id,
        CAST(customer_id AS VARCHAR) AS kunden_id, 
        CAST(treatment_date AS DATE) AS datum, 
        animal_name AS tier_name,
        species AS tierart, 
        diagnosis AS diagnose, 
        CAST(total_eur AS NUMERIC(10,2)) AS betrag_eur
    FROM staging.wald_behandlungen_clean

    UNION ALL

    -- Schmidt
    SELECT 
        (SELECT COUNT(*) FROM staging.juck_behandlungen_clean) + 
        (SELECT COUNT(*) FROM staging.wald_behandlungen_clean) + row_number() OVER () AS behandlung_id,
        3 AS praxis_id, 
        CAST(id AS VARCHAR) AS quell_id,
        kunde AS kunden_id, 
        strptime(datum, '%d.%m.%Y')::DATE AS datum,
        tier_name, 
        tier_art AS tierart, 
        leistung AS diagnose,
        CAST(REPLACE(REPLACE(betrag, ' EUR', ''), ',', '.') AS NUMERIC(10,2)) AS betrag_eur
    FROM staging.schm_behandlungen

    UNION ALL

    -- Bergblick (Praxis 4)
    SELECT 
        (SELECT COUNT(*) FROM staging.juck_behandlungen_clean) + 
        (SELECT COUNT(*) FROM staging.wald_behandlungen_clean) +
        (SELECT COUNT(*) FROM staging.schm_behandlungen) + 
        row_number() OVER () AS behandlung_id,
        4 AS praxis_id, 
        CAST(quell_zeile AS VARCHAR) AS quell_id,
        patient_id AS kunden_id, 
        CAST(datum AS DATE) AS datum, 
        tier_name, 
        tier_art AS tierart, 
        diagnose, 
        CAST(betrag_netto AS NUMERIC(10,2)) AS betrag_eur
    FROM staging.berg_behandlungen_clean  
    """
    con.execute(query_behandlung)

def zeige_finale_tabellen(con):
    print("\n" + "="*80)
    print(" FINALE NORM-TABELLEN AUSGEBEN")
    print("="*80)

    # Pandas Optionen setzen, damit keine Spalten abgeschnitten werden
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)

    print("\n--- Inhalt der Tabelle: transform.norm_kunde ---")
    df_kunde = con.execute("SELECT * FROM transform.norm_kunde").df()
    print(df_kunde)

    print("\n--- Inhalt der Tabelle: transform.norm_behandlung ---")
    df_behandlung = con.execute("SELECT * FROM transform.norm_behandlung").df()
    print(df_behandlung)

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

        # Tabellen vereinen
        erstelle_norm_tabellen(con)

        # Tabellen ausgeben
        zeige_finale_tabellen(con)

        print("\n Success: Alle Tabellen wurden bereinigt und erfolgreich in 'transform.norm_kunde' und 'transform.norm_behandlung' vereint")

    finally:
        con.close()

if __name__ == "__main__":
    main()
