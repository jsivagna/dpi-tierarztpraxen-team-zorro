# Profiling: praxis_bergblick.xml (Extrakt: Behandlungen)

## Datei
Ursprungsdatei: praxis_bergblick.xml
Format: XML (Hierarchische Baumstruktur)
Encoding: UTF-8
Zeilen (nach Flattening): 150

## Spalten / Felder
| Spalte | Typ-Vermutung | Beispiel | Distinct | Null% | Bemerkung |
|---|---|---|---|---|---|
| patient_id | Text | P-4191 | 115 | 0.00 | Fremdschlüssel zum Patienten (Foreign Key) |
| datum | Date | 2025-11-15 | 111 | 0.00 | ISO 8601 Format (YYYY-MM-DD) |
| diagnose | Categorical | Tumorabklaerung | 19 | 0.00 | Entspricht "Diagnose" / "Leistung" |
| netto | Real number (Float) | 162.92 | 150 | 0.00 | Netto-Betrag, englischer Dezimalpunkt |
| brutto | Real number (Float) | 193.87 | 150 | 0.00 | Brutto-Betrag, englischer Dezimalpunkt |

## Auffällige Muster
Die Behandlungsdaten sind am Ende der XML-Datei in einer eigenen Liste (`<behandlungen>`) gekapselt und wurden zu 150 flachen Datensätzen transformiert. Positiv fällt auf, dass das Datum dem sauberen ISO-Standard entspricht und die Beträge maschinenlesbar (ohne Suffix, mit Punkt) vorliegen. Die `patient_id` fungiert als sauberer Fremdschlüssel (115 Unique IDs bei 150 Behandlungen belegen eine realistische 1:n-Beziehung). Das Profiling-Tool meldet eine hohe Korrelation zwischen `netto` und `brutto`, was jedoch lediglich den konstanten Mehrwertsteuersatz (19 %) mathematisch abbildet.

## Datenqualitätsprobleme
* **Schema-Drift (Fehlende Denormalisierung):** Im Gegensatz zu den anderen Praxen fehlen in dieser Behandlungsdatei die Spalten zur Tier-Identifikation (`tier_name`, `tier_art`) komplett. Diese Informationen sind strikt in den Kunden-Datensätzen normalisiert. Vor einem praxenübergreifenden Verbund (UNION) muss zwingend ein interner `JOIN` zwischen dem Kunden- und dem Behandlungs-DataFrame durchgeführt werden, um diese fehlenden Spalten anzureichern.
* **Struktur (Fehlender Primary Key):** Den einzelnen Behandlungs-Knoten fehlt eine eindeutige, eigene Behandlungs-ID (wie z. B. `beh_nr` in Juckstadt). Beim Import muss zwingend ein künstlicher Schlüssel (Surrogate Key) generiert werden, um die Tabelle relational abzusichern.
* **Schema-Drift (Kosten-Aufschlüsselung):** Die Behandlungskosten sind aufgeteilt in zwei Attribute (`netto` und `brutto`). Die anderen Praxen weisen lediglich einen einzelnen Betrag aus. Vor einem UNION muss dies harmonisiert werden (z. B. Standardisierung auf den Brutto-Wert).
* **Schema-Drift (Spaltenbenennung):** Die Benennung der medizinischen Leistung lautet hier `diagnose`, was von Praxen wie Waldrand oder Schmidt abweicht (welche den Begriff `leistung` verwenden).
* **Struktur (Attribute vs. Elemente):** Sämtliche Metadaten (Datum, Patienten-ID, Beträge) verbergen sich in der Rohdatei in XML-Attributen und nicht in eigenen XML-Tags, was ein spezifisches Parsing erfordert.
* **Format (Datentyp ID):** Der Fremdschlüssel `patient_id` liegt als Text mit dem Präfix "P-" vor und muss vor einem Verbund mit rein numerischen IDs (wie Praxis Juckstadt) harmonisiert werden.