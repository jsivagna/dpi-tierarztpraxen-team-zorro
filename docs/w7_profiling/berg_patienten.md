# Profiling: praxis_bergblick_export.xml (Patienten)
## Datei
Ursprungsdatei: praxis_bergblick.xml
Format: XML (Hierarchische Baumstruktur)
Encoding: UTF-8
Zeilen (nach Flattening): 232

## Spalten / Felder
| Spalte | Typ-Vermutung | Beispiel | Distinct | Null% | Bemerkung |
|---|---|---|---|---|---|
| patient_id | Text | P-4002 | 232 | 0.00 | Unique Primary Key, Präfix "P-" |
| erfasst | Date | 2024-04-07 | 221 | 0.00 | ISO-Format (YYYY-MM-DD) |
| anrede | Categorical | Frau | 2 | 0.00 | "Herr" (126), "Frau" (106) |
| name | Text | Marion Hoffmann | 222 | 0.00 | Vor- und Nachname kombiniert |
| telefon | Text | 0645-02233 | 214 | 7.30 | |
| email | Text | hoffmann@email.de | 205 | 9.50 | Alle vorhandenen Werte enthalten ein "@" |
| strasse | Text | Kirchgasse 4 | - | 0.00 | Adressdaten aus XML extrahiert |
| plz | Text | 35500 | - | 0.00 | |
| ort | Text | Juckstadt | - | 0.00 | |
| tier_name | Categorical | Luna | 32 | 0.00 | |
| tier_art | Categorical | Katze | 2 | 0.00 | Katze (121), Hund (111) |

## Auffällige Muster
Da die Daten aus einer hierarchischen XML-Datei stammen, kapselt ein `<patient>`-Knoten sowohl die Halter- als auch die Tier- und Adressdaten. Diese wurden für das Profiling zu 232 flachen Datensätzen transformiert. Die Spalte `patient_id` fungiert als sauberer Unique Identifier. Eine Formatprüfung der vorhandenen E-Mail-Adressen verlief positiv (alle enthalten ein "@"-Zeichen).

## Datenqualitätsprobleme
* **Semantik (Geschlechter-Mismatch):** Eine algorithmische Überprüfung (vgl. Python-Library `gender-guesser`) zeigt erhebliche Diskrepanzen zwischen Vorname und Anrede. So wurden mindestens 16 weibliche Vornamen fälschlicherweise mit der Anrede "Herr" versehen (z. B. "Herr Julia Peters"). Umgekehrt existieren auch Mismatches bei männlichen Vornamen. *Hinweis:* Bei den 8 Datensätzen, die im Vornamen nur aus Initialen bestehen, konnte das Geschlecht naturgemäß nicht algorithmisch verifiziert werden.
* **Fehlwerte (XML-Spezifisch):** Bei fehlenden Kontaktinformationen fehlen 17 Einträge bei `telefon` (7,3 %) und 22 bei `email` (9,5 %). Das System nutzt hierfür teilweise leere Tags (`<telefon></telefon>`) oder den expliziten Nil-Namespace (`<email xsi:nil="true"/>`), was beim Import als `NULL` abgefangen werden muss.
* **Schema-Drift (Kombiniertes Namensfeld):** Der Name des Tierhalters steht in einem einzigen Textfeld (`name`). Im Vergleich zu Praxen wie Juckstadt oder Waldrand fehlen getrennte Spalten für Vor- und Nachname. Vor einem Verbund (UNION) muss dieser String zwingend gesplittet werden.
* **Schema-Drift (Fehlende Spalten):** Im Vergleich zur Praxis Waldrand fehlt hier das Datenfeld `marketing_consent` gänzlich. 
* **Vollständigkeit (Initialen):** Bei insgesamt 8 Datensätzen ist der Vorname im kombinierten Namensfeld nur als Initiale erfasst (z. B. "B. Schulz", "F. Lehmann"). 
* **Semantik (Tippfehler):** Es existiert eine extreme Häufung von offensichtlichen Buchstabendrehern in den Nachnamen (z. B. "Wlof", "Myeer", "Wenrer", "Wanger"), was beim späteren Entity Resolution zu massiven Problemen führen wird.
* **Format (Datentyp ID):** Die eindeutige ID liegt als Text mit dem Präfix "P-" vor und ist numerisch nicht direkt kompatibel zu reinen Integer-IDs (wie in Juckstadt).