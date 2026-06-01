# Profiling: praxis_juckstadt_kunden.csv

## Datei
Format: CSV
Trennzeichen: Semikolon (;)
Encoding: UTF-8
Header: ja
Zeilen: 223

## Spalten
| Spalte | Typ-Vermutung | Beispiel | Distinct | Null% | Bemerkung |
|---|---|---|---|---|---|
| kunden_nr | Real number | 112 | 223 | 0.00 | Eindeutig (Unique), Uniform verteilt |
| anrede | Categorical | Herr | 2 | 0.00 | |
| vorname | Text | - | 63 | 0.00 | |
| nachname | Categorical | Klein | 43 | 0.00 | |
| strasse | Text | - | 214 | 0.00 | |
| plz | Real number | 35502 | 8 | 0.00 | Hohe Korrelation mit `ort` |
| ort | Categorical | Juckstadt | 10 | 0.00 | Hohe Korrelation mit `plz` |
| telefon | Text | - | 222 | 0.00 | |
| email | Text | - | 196 | 9.4 | Lückenhaft (21 fehlende Werte) |
| angelegt_am | Date | 2019-01-07 | 215 | 0.00 | |

## Auffällige Muster
Der Datensatz umfasst 223 Zeilen. Die Spalte `kunden_nr` ist unique und gleichmäßig verteilt. Die einzig starke Korrelation besteht zwischen den Spalten `plz` und `ort`, was selbstverständlich ist. Das Datum reicht von Anfang 2019 bis Ende 2026.

## Datenqualitätsprobleme
* **Fehlwerte:** Bei der Spalte `email` fehlen 21 Einträge (9,4 %).
* **Semantik:** Bei min. 6 Einträgen haben weiblichen Vornamen fälschlicherweise "Herr." als Anrede hinterlegt. (Mit Python-Library "Gender-Guesser" ermittelt)
* **Vollständigkeit (Semantik):** Bei 4 Datensätzen ist der Vorname nicht ausgeschrieben, sondern nur als Initiale hinterlegt (z. B. "N. Schwarz", "B. Schaefer").