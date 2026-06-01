# Profiling: praxis_schmidt_kunden.csv
## Datei
Format: CSV
Trennzeichen: Pipe (|)
Encoding: UTF-8
Header: ja
Zeilen: 234

## Spalten
| Spalte | Typ-Vermutung | Beispiel | Distinct | Null% | Bemerkung |
|---|---|---|---|---|---|
| nachname | Categorical | Schneider | 45 | 0.00 | |
| vorname | Text | - | 68 | 0.00 | |
| anrede | Categorical | Fr. | 2 | 0.00 | Nutzt Abkürzungen (Fr./Hr.) |
| plz | Real number | 35564 | 8 | 0.00 | Hohe Korrelation mit `ort` |
| ort | Categorical | Wetzlar | 11 | 0.00 | Hohe Korrelation mit `plz` |
| strasse | Text | - | 225 | 0.00 | |
| tel | Text | - | 232 | 0.00 | |
| email | Text | - | 205 | 9.8 | Lückenhaft (23 fehlende Werte) |
| erfasst | Date | 2019-01-07 | 224 | 0.00 | |

## Auffällige Muster
Die Datei hat 234 Zeilen. Es fällt sofort auf, dass hier **keine eindeutige ID-Spalte** (wie `kunden_nr`) existiert. Zudem weichen die Spaltennamen (`tel`, `erfasst`) und die Werte-Semantik (`anrede` mit "Fr."/"Hr." statt "Frau"/"Herr") von den anderen Praxen ab (Schema-Drift).

## Datenqualitätsprobleme
* **Fehlwerte:** Bei der Spalte `email` fehlen 23 Einträge (9,8 %).
* **Struktur (Fehlende ID):** Fehlende Kunden-ID und abweichende Benennungen erschweren das direkte Zusammenführen mit anderen Tabellen.
* **Format (Datum):** Das Erfassungsdatum liegt im deutschen Format (DD.MM.YYYY) vor, was von den anderen Praxen abweicht.
* **Semantik (Geschlecht):** Bei min. 11 Einträgen ist bei weiblichen Vornamen fälschlicherweise "Hr." als Anrede hinterlegt (ermittelt mit der Python-Library "gender-guesser").
* **Dubletten:** Es existieren 36 Zeilendubletten (z. B. Sabine Hoffmann) mit lediglich abweichendem Erfassungsdatum.
* **Vollständigkeit (Semantik):** Bei insgesamt 8 Datensätzen besteht der Vorname lediglich aus Abkürzungen oder Initialen (z. B. "Th. Berger", "M. Lehmann").