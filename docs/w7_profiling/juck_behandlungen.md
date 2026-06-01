# Profiling: praxis_juckstadt_behandlungen.csv
## Datei
Format: CSV
Trennzeichen: Semikolon (;)
Encoding: UTF-8
Header: ja
Zeilen: 150

## Spalten
| Spalte | Typ-Vermutung | Beispiel | Distinct | Null% | Bemerkung |
|---|---|---|---|---|---|
| beh_nr | Integer | 1 | 150 | 0.00 | Eindeutig (Unique), Primary Key |
| datum | Date | 2025-09-01 | 114 | 0.00 | |
| patient_name | Text | Kitty | 32 | 0.00 | |
| kunde_nachname | Text | Stein | 38 | 0.00 | |
| diagnose | Text | Blutbild | 19 | 0.00 | |
| kosten_euro | Text | - | 150 | 0.00 | Eindeutig, aber als Text formatiert |

## Auffällige Muster
Der Datensatz ist mit exakt 150 Zeilen sehr vollständig. Die Spalte `beh_nr` fungiert als numerischer Primary Key. Auffällig ist jedoch das unsaubere Design der Tabellenbeziehung: Anstatt eines eindeutigen Fremdschlüssels (Kunden-ID) zur Kundentabelle wird lediglich der Nachname des Kunden (`kunde_nachname`) gespeichert.

## Datenqualitätsprobleme
* **Struktur (Referentielle Integrität):** Es fehlt eine `kunden_nr` als Fremdschlüssel. Die Zuordnung der Behandlungen zu den Kunden erfolgt nur über den Nachnamen. Dies führt zu Mehrdeutigkeiten und Matching-Fehlern, sobald mehrere Kunden denselben Nachnamen besitzen.
* **Format (Datentyp):** Die Geldbeträge in `kosten_euro` nutzen ein Komma als Dezimaltrenner (z. B. 191,17) und werden daher als Text (String) interpretiert. Sie müssen für Berechnungen zwingend in Floats konvertiert werden.
* **Schema-Drift:** Im Vergleich zur Praxis Waldrand fehlt hier eine explizite Spalte für die Tierart (`species`).
