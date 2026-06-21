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
            if df[col].dtype == 'object': # Nur wenn String
                # Ersetze Komma durch Punkt, entferne "EUR" oder "€" und wandle zu Float um
                df[col] = df[col].astype(str).str.replace(',', '.')
                df[col] = df[col].str.replace(r'[^\d.]', '', regex=True)
                df[col] = pd.to_numeric(df[col], errors='coerce')
                print(f"   Spalte '{col}' wurde zu Float (mit Punkt) transformiert.")

    # 4. Datums-Bereinigung (YYYY-MM-DD)
    for col in exakte_datum_spalten:
        if col in df.columns:
            # Erkennt Formate automatisch und wandelt in ISO-Strings um
            df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
            df[col] = df[col].dt.strftime('%Y-%m-%d')
            print(f"   Spalte '{col}' wurde in ISO-Format (YYYY-MM-DD) transformiert.")

    # 5. Bereinigte Daten als neue Tabelle zurück in DuckDB schreiben
    ziel_tabelle = f"{tabellen_name}_clean"
    con.execute(f"DROP TABLE IF EXISTS staging.{ziel_tabelle}")
    con.execute(f"CREATE TABLE staging.{ziel_tabelle} AS SELECT * FROM df")

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
                print(f"Tabelle {tab} nicht gefunden, wird übersprungen.")
                
        print("\n Success: Alle Tabellen wurden bereinigt und als '_clean' gespeichert.")
        
    finally:
        con.close()

if __name__ == "__main__":
    main()
