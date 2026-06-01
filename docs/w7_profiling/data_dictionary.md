# Unified Data Dictionary (Source-to-Target Mapping)

Dieses Data Dictionary mappt die Quell-Attribute der 4 heterogenen Systeme exakt auf das vorgegebene relationale Zieldatenmodell (`zielschema.sql`). 

*(Zeichenerklärung: `-` = Spalte existiert im Quellsystem nicht; `Drop` = Spalte existiert in der Quelle, wird aber für das Zielschema nicht übernommen)*

## 1. Zieltabelle: `final.verbund_kunde`

| Ziel-Spalte (SQL) | Datentyp | 🏥 Juckstadt (CSV) | 🌲 Waldrand (CSV) | 🔬 Schmidt (CSV) | ⛰️ Bergblick (XML) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **kunde_id** | SERIAL (PK) | `-` (Auto-generiert) | `-` (Auto-generiert) | `-` (Auto-generiert) | `-` (Auto-generiert) |
| **praxis_id** | INTEGER (FK) | 1 (Via `verbund_praxis`) | 2 (Via `verbund_praxis`) | 3 (Via `verbund_praxis`) | 4 (muss in Praxis-Tabelle angelegt werden!) |
| **quell_id** | VARCHAR(30) | `kunden_nr` | `customer_id` | `-` (Surrogate Key generieren) | `patient_id` |
| **anrede** | VARCHAR(20) | `anrede` | `-` | `anrede` | `anrede` |
| **vorname** | VARCHAR(50) | `vorname` | `first_name` | `vorname` | `name` (Kombiniert, Split nötig) |
| **nachname** | VARCHAR(50) | `nachname` | `last_name` | `nachname` | `name` (Kombiniert, Split nötig) |
| **strasse** | VARCHAR(100) | `strasse` | `street` | `strasse` | `strasse` |
| **plz** | VARCHAR(10) | `plz` | `zip_code` | `plz` | `plz` |
| **ort** | VARCHAR(50) | `ort` | `city` | `ort` | `ort` |
| **telefon_e164** | VARCHAR(20) | `telefon` (Transf. E164) | `phone` (Transf. E164) | `tel` (Transf. E164) | `telefon` (Transf. E164) |
| **email** | VARCHAR(100) | `email` | `email_address` | `email` | `email` |
| **erfasst_am** | DATE | `angelegt_am` (ISO) | `created_at` (Transf. ISO) | `erfasst` (Transf. ISO) | `erfasst` (ISO) |
| **dublette_von** | INTEGER (FK) | *Wird erst durch das LLM-Matching in W9 befüllt* | *Wird erst durch das LLM-Matching in W9 befüllt* | *Wird erst durch das LLM-Matching in W9 befüllt* | *Wird erst durch das LLM-Matching in W9 befüllt* |

*(Hinweis: Praxis-exklusive Felder wie `marketing_consent` bei Waldrand werden gemäß Zielschema im ETL-Prozess gedroppt.)*

---

## 2. Zieltabelle: `final.verbund_behandlung`

| Ziel-Spalte (SQL) | Datentyp | 🏥 Juckstadt (CSV) | 🌲 Waldrand (CSV) | 🔬 Schmidt (JSON) | ⛰️ Bergblick (XML) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **behandlung_id**| SERIAL (PK) | `-` (Auto-generiert) | `-` (Auto-generiert) | `-` (Auto-generiert) | `-` (Auto-generiert) |
| **praxis_id** | INTEGER (FK) | 1 (Via `verbund_praxis`) | 2 (Via `verbund_praxis`) | 3 (Via `verbund_praxis`) | 4 (Via `verbund_praxis`) |
| **quell_id** | VARCHAR(30) | `beh_nr` | `treatment_id` | `id` | `-` (Surrogate Key generieren) |
| **kunde_id** | INTEGER (FK) | `-` (via Entity Matching) | `customer_id` (via Join) | `-` (via Entity Matching) | `patientId` (via Join) |
| **datum** | DATE | `datum` (ISO) | `treatment_date` (Transf.) | `datum` (Transf. ISO) | `datum` (ISO) |
| **tier_name** | VARCHAR(50) | `patient_name` | `animal_name` | `tier.name` | `<tier><name>` (via internem Join) |
| **tierart** | VARCHAR(20) | `-` | `species` (Transf. zu DE) | `tier.art` | `<tier><art>` (via internem Join) |
| **diagnose** | TEXT | `diagnose` | `diagnosis` | `leistung` | `diagnose` |
| **betrag_eur** | NUMERIC(10,2) | `kosten_euro` (Transf. Float) | `total_eur` | `betrag` (Transf. Float) | `brutto` |

*(Hinweis: Praxis-exklusive Felder wie `<geburt>` bei Bergblick werden gemäß Zielschema im ETL-Prozess gedroppt.)*

---

## 3. Zieltabelle: `final.verbund_praxis` (Stammdaten)
Diese Tabelle fungiert als Dimensionstabelle (Referenz) für die `praxis_id`.

* **1** = JUCK (Tierarztpraxis Canini, Juckstadt)
* **2** = WALD (Kleintierpraxis Waldrand, Rabenau)
* **3** = SCHM (Tierarztzentrum Schmidt, Wetzlar)
* **4** = BERG (Tierklinik Bergblick, Waldrand) -> *Muss im Load-Skript manuell nachgetragen werden, da im DDL-Insert fehlend!*