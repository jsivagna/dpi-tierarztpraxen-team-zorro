import duckdb
import pandas as pd

def main():
    print("Starte Vector-Search...")

    # Datenbank verbinden und VSS laden
    con = duckdb.connect("verbund.duckdb")
    con.execute("INSTALL vss;")
    con.execute("LOAD vss;")

    # 1. Alle Kunden laden (jetzt inklusive der globalen kunde_id)
    kunden = con.execute("""
        SELECT kunde_id, praxis_id, quell_id, quell_text, embedding 
        FROM transform.kunden_embeddings
    """).df()
    
    print(f"Suche für {len(kunden)} Kunden die 10 nächsten Nachbarn (KNN)...")

    kandidaten_liste = []
    gesehene_paare = set() # verhindert doppelte Suche von Dubletten (A-B und B-A)

    # 2. Pro Kunden die 10 nächsten Nachbarn suchen
    for index, row in kunden.iterrows():
        # list_cosine_distance misst Entfernung -> Je kleiner/näher an 0, desto ähnlicher.
        nachbarn = con.execute(f"""
            SELECT kunde_id, praxis_id, quell_id, quell_text,
                   list_cosine_distance(embedding, ?::FLOAT[768]) as distanz
            FROM transform.kunden_embeddings
            WHERE kunde_id != {row['kunde_id']}  -- Eigener Datensatz wird ausgeschlossen
            ORDER BY distanz ASC
            LIMIT 10
        """, [row['embedding']]).df()

        for _, nachbar in nachbarn.iterrows():
            # Grenzwert: Distanz < 0.14 
            if nachbar['distanz'] < 0.14:
                
                # Eindeutige ID für potenzielle Dubletten (jetzt sauber mit der kunde_id)
                paar_id = tuple(sorted([row['kunde_id'], nachbar['kunde_id']]))

                if paar_id not in gesehene_paare:
                    gesehene_paare.add(paar_id)
                    kandidaten_liste.append({
                        'kunde_a_id': row['kunde_id'],
                        'kunde_a_praxis': row['praxis_id'],
                        'kunde_a_quell_id': row['quell_id'],
                        'kunde_a_text': row['quell_text'],
                        
                        'kunde_b_id': nachbar['kunde_id'],
                        'kunde_b_praxis': nachbar['praxis_id'],
                        'kunde_b_quell_id': nachbar['quell_id'],
                        'kunde_b_text': nachbar['quell_text'],
                        
                        'distanz': nachbar['distanz']
                    })

    df_kandidaten = pd.DataFrame(kandidaten_liste)

    # 3. In Datenbank speichern (im transform-Schema)
    print("Speichere Kandidatenpaare für das LLM in transform.kandidaten_paare...")
    con.execute("DROP TABLE IF EXISTS transform.kandidaten_paare")
    
    # Prüfen, ob überhaupt Kandidaten gefunden wurden, um Abstürze zu vermeiden
    if not df_kandidaten.empty:
        con.execute("CREATE TABLE transform.kandidaten_paare AS SELECT * FROM df_kandidaten")
        print(f"\n Verdächtigste Kandidatenpaare herausgefiltert: {len(df_kandidaten)} ")

        # 4. Zeige die Top 3
        print("\nVorschau der Top 3 Kandidatenpaare:")
        print("-" * 80)
        top_3 = df_kandidaten.sort_values(by='distanz').head(3)
        for _, row in top_3.iterrows():
            print(f"Distanz: {row['distanz']:.4f} (Je kleiner, desto ähnlicher)")
            print(f"A [Global-ID {row['kunde_a_id']} | Praxis {row['kunde_a_praxis']} | {row['kunde_a_quell_id']}]: {row['kunde_a_text'][:90]}...")
            print(f"B [Global-ID {row['kunde_b_id']} | Praxis {row['kunde_b_praxis']} | {row['kunde_b_quell_id']}]: {row['kunde_b_text'][:90]}...")
            print("-" * 80)
    else:
        print("\n Keine Kandidatenpaare mit einer Distanz < 0.14 gefunden.")
        # Leere Tabelle anlegen, damit spätere Skripte nicht abstürzen
        con.execute("""
            CREATE TABLE transform.kandidaten_paare (
                kunde_a_id BIGINT, kunde_a_praxis INTEGER, kunde_a_quell_id VARCHAR, kunde_a_text VARCHAR,
                kunde_b_id BIGINT, kunde_b_praxis INTEGER, kunde_b_quell_id VARCHAR, kunde_b_text VARCHAR,
                distanz DOUBLE
            )
        """)

    con.close()

if __name__ == "__main__":
    main()
