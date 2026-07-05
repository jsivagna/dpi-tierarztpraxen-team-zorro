import json
import time
from typing import Literal

import duckdb
import ollama
from pydantic import BaseModel, Field, ValidationError

# ============================================================
# KONFIGURATION
# ============================================================
DB = "verbund.duckdb"
MODEL = "qwen2.5:7b-instruct" # Das Instruct-Modell ist besser für JSON!
MAX_PAARE = 30                # Zum Testen auf 50 limitiert (damit du nicht auf 3500 warten musst)
MAX_RETRIES = 0               # bei kaputtem JSON erneut fragen
TEMPERATURE = 0.0             # deterministische Antworten

# ============================================================
# 1. Pydantic-Schema (Strikte Vorgaben wie beim Prof)
# ============================================================
class MatchEntscheidung(BaseModel):
    """Strukturierte Antwort des LLM zu einem Kandidatenpaar."""
    is_duplicate: bool = Field(
        description="True, wenn beide Datensaetze dieselbe Person beschreiben."
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Sicherheit der Einschaetzung zwischen 0.0 und 1.0.",
    )
    reasoning: str = Field(
        min_length=10, max_length=400,
        description="1-2 Saetze Begruendung, welches Merkmal entschieden hat.",
    )
    decisive_signal: Literal["name", "address", "phone", "email", "combined"] = Field(
        description="Das ausschlaggebende Merkmal fuer die Entscheidung.",
    )

# ============================================================
# 2. Prompt-Konstruktion
# ============================================================
SYSTEM_PROMPT = """Du bist ein Datenintegrator. Du bekommst zwei Kundendatensaetze
aus unterschiedlichen Praxen und entscheidest, ob es sich um
dieselbe reale Person handelt.

Achte besonders auf:
  - Namens-Varianten (Initialen, abgekuerzte Vornamen, Reihenfolge)
  - Adress-Varianten (Strasse/Str., Schreibweise der PLZ)
  - Telefon und E-Mail als starke Signale
  - Plausibilitaet als Ganzes

Antworte ausschliesslich als JSON nach dem vorgegebenen Schema.
Begruende kurz, welches Merkmal entscheidend war."""

def build_user_prompt(a_text: str, b_text: str) -> str:
    return f"Datensatz A: {a_text}\nDatensatz B: {b_text}"

# ============================================================
# 3. LLM-Aufruf mit Retry-Logik
# ============================================================
def klassifiziere(a_text: str, b_text: str) -> MatchEntscheidung:
    """Fragt das LLM und gibt eine validierte MatchEntscheidung zurueck."""
    schema = MatchEntscheidung.model_json_schema()
    user_msg = build_user_prompt(a_text, b_text)

    last_err = None
    for versuch in range(1, MAX_RETRIES + 2):
        try:
            resp = ollama.chat(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg},
                ],
                format=schema,
                options={"temperature": TEMPERATURE},
            )
            return MatchEntscheidung.model_validate_json(resp["message"]["content"])
        except (ValidationError, json.JSONDecodeError) as exc:
            last_err = exc
            print(f"  [Versuch {versuch}] LLM-Antwort ungueltig: {exc}")
            time.sleep(1)
            continue
    raise RuntimeError(f"LLM lieferte nach {MAX_RETRIES + 1} Versuchen kein gueltiges JSON: {last_err}")

# ============================================================
# 4. Pipeline-Lauf
# ============================================================
def main():
    con = duckdb.connect(DB)
    
    # Ergebnis-Tabelle anlegen (Nutzt nun BIGINT für unsere kunde_id)
    # Schema embeddings wird erstellt, falls es nicht existiert
    con.execute("CREATE SCHEMA IF NOT EXISTS embeddings;")
    con.execute("""
        CREATE OR REPLACE TABLE embeddings.match_entscheidung (
            a_id            BIGINT,
            b_id            BIGINT,
            sim             FLOAT,
            is_duplicate    BOOLEAN,
            confidence      FLOAT,
            reasoning       VARCHAR,
            decisive_signal VARCHAR,
            modell          VARCHAR,
            entschieden_am  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Paare aus unserer vorbereiteten Tabelle laden (mit angepassten Spaltennamen)
    # Distanz wird hier in Ähnlichkeit (sim) umgerechnet: 1.0 - distanz
    paare = con.execute(f"""
        SELECT 
            kunde_a_id AS a_id, 
            kunde_b_id AS b_id, 
            kunde_a_text AS a_text, 
            kunde_b_text AS b_text, 
            (1.0 - distanz) AS sim
        FROM transform.kandidaten_paare
        ORDER BY distanz ASC
        LIMIT {MAX_PAARE}
    """).fetchall()

    if not paare:
        print("Keine Kandidatenpaare in 'transform.kandidaten_paare' gefunden!")
        return

    print(f"Bewerte die Top {len(paare)} Kandidatenpaare mit {MODEL} ...\n")
    t0 = time.time()
    
    for a_id, b_id, a_text, b_text, sim in paare:
        try:
            entscheidung = klassifiziere(a_text, b_text)
        except RuntimeError as e:
            print(f"  {a_id} vs {b_id}: SKIP ({e})")
            continue

        # In die Datenbank schreiben
        con.execute(
            """INSERT INTO embeddings.match_entscheidung 
               (a_id, b_id, sim, is_duplicate, confidence, reasoning, decisive_signal, modell) 
               VALUES (?,?,?,?,?,?,?,?)""",
            [a_id, b_id, sim, entscheidung.is_duplicate, entscheidung.confidence, 
             entscheidung.reasoning, entscheidung.decisive_signal, MODEL]
        )

        # Konsolenausgabe wie vom Prof gewünscht
        mark = "🟢 MATCH" if entscheidung.is_duplicate else "🔴 KEIN MATCH   "
        print(f" {mark} | IDs: {a_id} vs {b_id} | sim={sim:.3f} | conf={entscheidung.confidence:.2f} | signal={entscheidung.decisive_signal}")
        print(f"          A: {a_text[:80]}...")
        print(f"          B: {b_text[:80]}...")
        print(f"          -> {entscheidung.reasoning}\n")

    dt = time.time() - t0
    print(f"Fertig in {dt:.1f}s ({dt / len(paare):.1f}s pro Paar).")

    # Zusammenfassung
    summary = con.execute("""
        SELECT 
            COUNT(*) AS gesamt,
            SUM(CASE WHEN is_duplicate THEN 1 ELSE 0 END) AS matches,
            ROUND(AVG(confidence), 2) AS conf_avg
        FROM embeddings.match_entscheidung
    """).fetchone()
    
    print(f"\n Gesamt bewertet: {summary[0]} | Als Dubletten erkannt: {summary[1]} | Ø Confidence: {summary[2]}")
    con.close()

if __name__ == "__main__":
    main()
