# Profiling: praxis_waldrand_behandlungen.csv
## Datei
Format: CSV
Trennzeichen: Komma (,)
Encoding: UTF-8
Header: ja
Zeilen: 150

## Spalten
| Spalte | Typ-Vermutung | Beispiel | Distinct | Null% | Bemerkung |
|---|---|---|---|---|---|
| treatment_id | Text | - | 150 | 0.00 | Eindeutige ID (Unique) |
| customer_id | Text | - | 108 | 0.00 | Fremdschlüssel zum Kunden |
| animal_name | Categorical | Luna | 32 | 0.00 | Hohe Korrelation mit `species` |
| species | Categorical | cat | 2 | 0.00 | Nur "cat" und "dog" |
| treatment_date | Date | 2025-09-02 | 116 | 0.00 | |
| diagnosis | Categorical | Check-up | 19 | 0.00 | Englische Werte |
| total_eur | Real number | 114.89 | 150 | 0.00 | Korrekt als Zahl erkannt (Punkt als Trenner) |

## Auffällige Muster
Die Datei ist mit 150 Zeilen vollständig. Im Gegensatz zu Juckstadt wurden die Beträge (`total_eur`) hier direkt korrekt als Zahlen eingelesen, da ein Punkt als Dezimaltrenner genutzt wird. Positiv fällt auf, dass eine saubere Fremdschlüsselbeziehung (`customer_id`) zur Kundentabelle existiert.

## Datenqualitätsprobleme
* **Format (Datentypen ID):** Die ID-Spalten (`treatment_id`, `customer_id`) liegen als Text (Strings mit Präfixen wie "T" oder "W-") vor, nicht als Integer wie bei Juckstadt. Dies erfordert eine Bereinigung.
* **Format (Datum):** Das Datumsformat in `treatment_date` weicht vom ISO-Standard ab und liegt im US-Format (MM/DD/YYYY) vor.
* **Schema-Drift:** Sämtliche Spaltennamen (`treatment_id`, `species`, etc.) sowie die Kategorien und Freitexte (z. B. "cat", "Check-up") sind englischsprachig.
* **Struktur (Zusätzliche Spalte):** Die Tabelle enthält eine Spalte `species` zur Klassifizierung der Tierart, die in der Juckstadt-Tabelle fehlt.