import duckdb
import pandas as pd

def main():
    print("Starte Vector-Search...")
    
    # Datenbank verbinden und VSS laden
    con = duckdb.connect("verbund.duckdb")
    con.execute("INSTALL vss;")
    con.execute("LOAD vss;")

    # Alle Kunden laden
    kunden = con.execute("SELECT praxis, quell_zeile, quell_text, embedding FROM staging.kunden_embeddings").df()
    print(f"Suche für {len(kunden)} Kunden die nächsten Nachbarn...")
    
    kandidaten_liste = []
    gesehene_paare = set() # verhindert doppelte Suche von Dubletten

    # Pro Kunden die 10 nächsten Nachbarn suchen
    for index, row in kunden.iterrows():
        # list_cosine_distance misst Entfernung -> Je kleiner/näher an 0, desto ähnlicher.
        nachbarn = con.execute(f"""
            SELECT praxis, quell_zeile, quell_text, 
                   list_cosine_distance(embedding, ?::FLOAT[768]) as distanz
            FROM staging.kunden_embeddings
            WHERE NOT (praxis = '{row['praxis']}' AND quell_zeile = {row['quell_zeile']})
            ORDER BY distanz ASC
            LIMIT 10  
        """, [row['embedding']]).df()

        for _, nachbar in nachbarn.iterrows():
            # Nur speichern, wenn ähnlich -> Grenzwert: Distanz < 0.25
            if nachbar['distanz'] < 0.25:
                # eindeutige ID für potenzielle Dubletten
                paar_id = tuple(sorted([f"{row['praxis']}_{row['quell_zeile']}", f"{nachbar['praxis']}_{nachbar['quell_zeile']}"]))
                
                if paar_id not in gesehene_paare:
                    gesehene_paare.add(paar_id)
                    kandidaten_liste.append({
                        'kunde_a_praxis': row['praxis'],
                        'kunde_a_zeile': row['quell_zeile'],
                        'kunde_a_text': row['quell_text'],
                        'kunde_b_praxis': nachbar['praxis'],
                        'kunde_b_zeile': nachbar['quell_zeile'],
                        'kunde_b_text': nachbar['quell_text'],
                        'distanz': nachbar['distanz']
                    })

    df_kandidaten = pd.DataFrame(kandidaten_liste)
    print(f"\n Verdächtigsten Kandidatenpaare herausgefiltert: {len(df_kandidaten)} ")
    
    # Zeige die Top 3
    print("\n👀 Vorschau:")
    print("-" * 70)
    top_3 = df_kandidaten.sort_values(by='distanz').head(3)
    for _, row in top_3.iterrows():
        print(f"Distanz: {row['distanz']:.4f} (Je kleiner, desto ähnlicher)")
        print(f"A [{row['kunde_a_praxis']}]: {row['kunde_a_text'][:100]}...")
        print(f"B [{row['kunde_b_praxis']}]: {row['kunde_b_text'][:100]}...")
        print("-" * 70)

    con.close()

if __name__ == "__main__":
    main()
