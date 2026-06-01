# Profiling: praxis_schmidt_behandlungen.json
## Datei
Format: JSON
Encoding: UTF-8
Struktur: Verschachtelt (Nested JSON, geparst zu 7 flachen Spalten)
Zeilen: 150

## Spalten
| Spalte | Typ-Vermutung | Beispiel | Distinct | Null% | Bemerkung |
|---|---|---|---|---|---|
| id | Integer | 301 | 150 | 0.00 | Eindeutige Behandlungs-ID (301-450) |
| datum | Date | 24.09.2025 | 108 | 0.00 | Deutsches Format (DD.MM.YYYY) |
| kunde | Text | Schneider X. | 104 | 0.00 | Nachname + Initiale (kein Fremdschlüssel) |
| leistung | Categorical | Kontrolle | 19 | 0.00 | Entspricht "Diagnose" |
| betrag | Text | 15,46 EUR | 148 | 0.00 | Enthält Währungssymbol und Komma |
| tier.name | Categorical | Caesar | 32 | 0.00 | Aus Unterobjekt `tier` extrahiert |
| tier.art | Categorical | Katze | 2 | 0.00 | Uniform verteilt (Exakt 50 % Katze, 50 % Hund) |

## Auffällige Muster
Der Datensatz ist mit 150 Zeilen und 0 fehlenden Werten vollständig. Auffällig ist die JSON-typische hierarchische Struktur (`tier.name`, `tier.art`), die beim Import "flachgeklopft" (Flattening) werden muss. Die Spalte `id` ist ein sauberer, fortlaufender Primary Key für die Behandlungen. Die Tierarten sind exakt gleichmäßig verteilt (75 Hunde, 75 Katzen). Das Profiling-Tool meldet starke Korrelationen (z. B. zwischen Tiername und Tierart). Dies stellt jedoch keinen Datenfehler dar, sondern spiegelt natürliche funktionale Abhängigkeiten wider.

## Datenqualitätsprobleme
* **Struktur (Verschachtelung):** Die Daten liegen nicht tabellarisch vor. Das Objekt `tier` muss beim Import in zwei getrennte Spalten aufgelöst werden.
* **Struktur (Fehlender Fremdschlüssel & Asymmetrie):** Es fehlt eine eindeutige Kunden-ID. Die Zuordnung der Behandlungen erfolgt rein textbasiert und asymmetrisch zur Kundentabelle: In den Behandlungen steht "Nachname + Initiale" (z. B. "Schneider X."), während in der Kundentabelle "Vorname + Nachname" steht. Ein direkter Tabellen-Join ist somit unmöglich und erfordert aufwändiges String-Matching (Entity Resolution), was bei Namensgleichheiten zu Datenverlust führt.
* **Format (Datentyp Währung):** Die Spalte `betrag` wird als Text-String interpretiert, da sie die Einheit " EUR" enthält und ein Komma als Trenner nutzt. Für Berechnungen müssen das Suffix entfernt und das Komma in einen Punkt gewandelt werden.
* **Format (Datum):** Das Datum weicht vom ISO-Standard ab und liegt im deutschen Format (`DD.MM.YYYY`) vor.
* **Schema-Drift:** Abweichende Benennung der Spalte für die Diagnose (`leistung`).
* **Semantik (Tippfehler):** Ein Blick in die Beispieldaten zeigt offensichtliche Schreibfehler bei den Kundennamen (z. B. "Muleler I." statt "Mueller I."), was das textbasierte Matching weiter erschwert.