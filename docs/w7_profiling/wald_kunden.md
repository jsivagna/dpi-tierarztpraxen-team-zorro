# Profiling: praxis_waldrand_kunden.csv

## Datei
Format: CSV
Trennzeichen: Komma (,)
Encoding: UTF-8
Header: ja
Zeilen: 227

## Spalten
| Spalte | Typ-Vermutung | Beispiel | Distinct | Null% | Bemerkung |
|---|---|---|---|---|---|
| customer_id | Text | - | 227 | 0.00 | Eindeutige ID (Unique) |
| first_name | Text | - | 64 | 0.00 | |
| last_name | Categorical | Albrecht | 47 | 0.4 | 1 fehlender Wert |
| street | Text | - | 216 | 0.00 | |
| zip_code | Real number | 35474 | 8 | 0.00 | Hohe Korrelation mit `city` |
| city | Categorical | Rabenau | 11 | 0.00 | Hohe Korrelation mit `zip_code` |
| phone | Text | - | 227 | 0.00 | Eindeutig (Unique) |
| email_address | Text | - | 175 | 22.0 | Lückenhaft (50 fehlende Werte) |
| created_at | Text | - | 212 | 0.00 | Als Text eingelesen (wg. Format) |
| marketing_consent | Boolean | True | 2 | 33.0 | Neue Spalte, stark lückenhaft |

## Auffällige Muster
Die Datei umfasst 227 Zeilen. Wie schon bei den Behandlungsdaten dieser Praxis fallen die englischen Spaltennamen auf (Schema-Drift). Zudem gibt es hier eine völlig neue Spalte `marketing_consent` (Boolean), die in den anderen Praxen nicht existiert. Auffällig ist auch, dass das Datum `created_at` vom Profiler als reiner Text und nicht als Datum (Date) erkannt wurde. Dies ist ein starkes Indiz für das amerikanische Format (MM/DD/YYYY).

## Datenqualitätsprobleme
* **Format (Datentyp ID):** Die Kunden-ID liegt durch das Präfix "W-" als Text (String) vor und ist nicht direkt kompatibel mit den numerischen IDs (Integer) der anderen Praxen.
* **Fehlwerte:** Starker Anteil fehlender Werte bei `marketing_consent` (33,0 %) und `email_address` (22,0 %). Außerdem fehlt bei einem Datensatz der Nachname (0,4 %).
* **Schema-Drift:** Englische Spaltennamen, das Fehlen einer `anrede`-Spalte und das Vorhandensein einer praxisexklusiven Spalte (`marketing_consent`) führen bei einem späteren Verbund (UNION) zu Problemen.
* **Format (Datum):** Das Datumsformat in `created_at` weicht vom ISO-Standard ab und wird daher zunächst als normaler Text-String interpretiert.
* **Format (Datum/Invalidität):** Neben dem abweichenden US-Format (MM/DD/YYYY) enthalten mindestens 5 Einträge in der Spalte `created_at` einen simplen Bindestrich ("-") anstelle eines gültigen Kalenderdatums. Dies führt zu Fehlern beim Parsen.
* **Format (Telefon):** Extreme Inkonsistenz bei allen Telefonnummern (+49, Schrägstriche, Leerzeichen).
* **Semantik (Tippfehler):** Auffällig viele Buchstabendreher in den Nachnamen (Pteers, Wagenr, Kohc), was auf manuelle Eingabefehler hindeutet.
* **Vollständigkeit (Semantik):** Bei 5 Datensätzen ist der Vorname nur als Initiale erfasst (z. B. "F. Hofmann", "V. Schaefer"). Besonders kritisch ist hierbei ein Fall ("K."), bei dem zusätzlich der Nachname komplett fehlt (`NaN`).