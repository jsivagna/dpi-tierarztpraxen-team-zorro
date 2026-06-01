# Zentrale Fehlerliste (Data Quality Issues)

Diese Liste dokumentiert die identifizierten Datenqualitätsprobleme über alle 8 Quelltabellen hinweg, strukturiert nach den vorgegebenen Kategorien.

## 1. Schema-Drift (Strukturelle Abweichungen)
1. **Waldrand (Sprache):** Verwendet als einzige Praxis ausschließlich englische Spaltennamen (z. B. `customer_id`, `species`).
2. **Waldrand (Exklusive Spalte):** Enthält als einzige Praxis die Spalte `marketing_consent`, die bei einem UNION mit den anderen Praxen fehlt.
3. **Bergblick (Denormalisierung):** Die Tierdaten (Name, Art, Alter) fehlen in den Behandlungsdaten komplett, da sie im XML an das Kunden-Objekt gebunden sind.
4. **Bergblick (Kombiniertes Feld):** Vor- und Nachname des Kunden stehen in einem einzigen XML-Tag (`<name>`), während alle anderen Praxen diese trennen.
5. **Schmidt (Fehlender Primary Key):** Der Kunden-Tabelle (CSV) fehlt jegliche eindeutige Kunden-ID.
6. **Schmidt (Fehlender Foreign Key):** In den Behandlungsdaten (JSON) fehlt eine Kunden-ID zur Verknüpfung. Die Zuordnung erfolgt nur über einen asymmetrischen String ("Nachname + Initiale").
7. **Juckstadt (Fehlender Foreign Key):** Auch hier fehlt die `kunden_nr` in den Behandlungen; die Verknüpfung erfolgt unsauber über den Nachnamen des Tieres/Kunden.
8. **Bergblick (Fehlender Primary Key):** Den XML-Behandlungsknoten fehlt eine eigene, eindeutige Behandlungs-ID.
9. **Bergblick (Kosten-Split):** Behandlungskosten sind in `netto` und `brutto` aufgeteilt; die anderen Praxen haben nur einen Gesamtbetrag.
10. **Juckstadt (Fehlende Tierart):** In den Behandlungen von Juckstadt fehlt die Spalte für die Tierart (Hund/Katze) komplett.

## 2. Format
11. **Datentyp ID-Inkonsistenz:** Juckstadt nutzt Integer für IDs (z. B. `1`), Waldrand nutzt Text-Strings mit Präfix (`W-100`), Bergblick nutzt Text-Strings mit Präfix (`P-4001`).
12. **Datumsformat (US):** Waldrand nutzt in `created_at` und `treatment_date` das US-Format (MM/DD/YYYY).
13. **Datumsformat (DE):** Schmidt nutzt das deutsche Format (DD.MM.YYYY) statt ISO 8601.
14. **Datumsformat (Invalidität):** Bei Waldrand enthalten mind. 5 Einträge in `created_at` einen simplen Bindestrich ("-") statt eines Datums.
15. **Datentyp Währung (Komma/Text):** Bei Schmidt enthält der Betrag Text (" EUR") und ein Komma ("15,46 EUR") und wird als String geparst.
16. **Datentyp Währung (Komma):** Auch Juckstadt nutzt ein Komma als Dezimaltrenner bei den Beträgen, was beim Import als String (Text) interpretiert wird.
17. **Telefonnummern:** Extreme formelle Inkonsistenzen über alle Praxen hinweg (+49, Leerzeichen, Schrägstriche).

## 3. Encoding
18. **Encoding-Status:** Alle Dateien (CSV, XML, JSON) ließen sich fehlerfrei als UTF-8 decodieren. Es wurden keine typischen ISO-8859-1 Zeichensalat-Fehler (z. B. "Ã¼" statt "ü") gefunden. 

## 4. Fehlwerte (Null-Values)
19. **Kunden-Emails:** Massive Lücken über alle Praxen hinweg (Juckstadt: 9,4 %, Schmidt: 9,8 %, Waldrand: 22,0 %). In Bergblick fehlen 9,5 % (maskiert als XML-Nil: `xsi:nil="true"`).
20. **Marketing Consent:** Bei Waldrand fehlen 33 % der Einträge in dieser Spalte.
21. **Kontakttelefon:** Bei Bergblick fehlen 17 Telefonnummern (leere XML-Tags `<telefon></telefon>`).
22. **Fehlender Nachname:** Bei einem Datensatz in Waldrand fehlt der Nachname komplett (`NaN`).

## 5. Dubletten
23. **Zeilendubletten (Schmidt):** In der Kundentabelle Schmidt existieren exakt 36 Zeilendubletten (gleicher Name, Ort, etc.), die sich ausschließlich durch ein abweichendes Erfassungsdatum unterscheiden.

## 6. Semantik (Inhaltliche & Logische Fehler)
24. **Geschlechter-Mismatch (Anrede):** In Juckstadt, Schmidt und massiv in Bergblick (16 Fälle) passt die vergebene Anrede ("Herr" / "Hr.") nicht zu offensichtlich weiblichen Vornamen (nachgewiesen durch Gender-Guesser). Gleiches gilt umgekehrt für männliche Vornamen.
25. **Tippfehler (Namen):** Hohe Dichte an Buchstabendrehern in Waldrand ("Pteers"), Schmidt ("Muleler") und Bergblick ("Wlof", "Wanger"), was ein deterministisches Entity-Matching massiv behindert.
26. **Initialen statt Namen:** Über alle 4 Praxen hinweg bestehen Vornamen teilweise nur aus Initialen (z. B. "F. Lehmann", "Th. Berger", "K.").