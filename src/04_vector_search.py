import duckdb
import pandas as pd

def main():
    print("Starte Vector-Search...")

    # Datenbank verbinden und VSS laden
    con = duckdb.connect("verbund.duckdb")
    con.execute("INSTALL vss;")
    con.execute("LOAD vss;")

    # Alle Kunden laden (jetzt mit praxis_id und quell_id)
    kunden = con.execute("SELECT praxis_id, quell_id, quell_text, embedding FROM staging.kunden_embeddings").df()
    print(f"Suche für {len(kunden)} Kunden die 10 nächsten Nachbarn (KNN)...")

    kandidaten_liste = []
    gesehene_paare = set() # verhindert doppelte Suche von Dubletten

    # Pro Kunden die 10 nächsten Nachbarn suchen
    for index, row in kunden.iterrows():
        # list_cosine_distance misst Entfernung -> Je kleiner/näher an 0, desto ähnlicher.
        nachbarn = con.execute(f"""
            SELECT praxis_id, quell_id, quell_text,
                   list_cosine_distance(embedding, ?::FLOAT[768]) as distanz
            FROM staging.kunden_embeddings
            WHERE NOT (praxis_id = {row['praxis_id']} AND quell_id = '{row['quell_id']}')
            ORDER BY distanz ASC
            LIMIT 10
        """, [row['embedding']]).df()

        for _, nachbar in nachbarn.iterrows():
            # Grenzwert: Distanz < 0.15 (erfasst auch leichte Tippfehler)
            if nachbar['distanz'] < 0.15:
                # Eindeutige ID für potenzielle Dubletten
                paar_id = tuple(sorted([f"{row['praxis_id']}_{row['quell_id']}", f"{nachbar['praxis_id']}_{nachbar['quell_id']}"]))

                if paar_id not in gesehene_paare:
                    gesehene_paare.add(paar_id)
                    kandidaten_liste.append({
                        'kunde_a_praxis': row['praxis_id'],
                        'kunde_a_id': row['quell_id'],
                        'kunde_a_text': row['quell_text'],
                        'kunde_b_praxis': nachbar['praxis_id'],
                        'kunde_b_id': nachbar['quell_id'],
                        'kunde_b_text': nachbar['quell_text'],
                        'distanz': nachbar['distanz']
                    })

    df_kandidaten = pd.DataFrame(kandidaten_liste)
    
    # NEU: In Datenbank speichern für den kommenden LLM-Schritt
    print("Speichere Kandidatenpaare für das LLM in staging.kandidaten_paare...")
    con.execute("DROP TABLE IF EXISTS staging.kandidaten_paare")
    con.execute("CREATE TABLE staging.kandidaten_paare AS SELECT * FROM df_kandidaten")
    
    print(f"\n✅ Verdächtigste Kandidatenpaare herausgefiltert: {len(df_kandidaten)} ")

    # Zeige die Top 3
    print("\n👀 Vorschau der Top 3 Kandidatenpaare:")
    print("-" * 80)
    top_3 = df_kandidaten.sort_values(by='distanz').head(3)
    for _, row in top_3.iterrows():
        print(f"Distanz: {row['distanz']:.4f} (Je kleiner, desto ähnlicher)")
        print(f"A [Praxis {row['kunde_a_praxis']} | ID {row['kunde_a_id']}]: {row['kunde_a_text'][:90]}...")
        print(f"B [Praxis {row['kunde_b_praxis']} | ID {row['kunde_b_id']}]: {row['kunde_b_text'][:90]}...")
        print("-" * 80)

    con.close()

if __name__ == "__main__":
    main()
