# Testprotokoll: KI-gestützte Dublettenerkennung (Meilenstein W9)

Dieses Dokument fasst die Ergebnisse des zweistufigen Matching-Prozesses (Vector-Search + LLM-Judge) zusammen. Die Pipeline vergleicht heterogene Kundendatensätze aus vier verschiedenen Tierarztpraxen.

---

## 1. Phase: Vector-Search (Kandidatensuche)

Im ersten Schritt wurde der `nomic-embed-text` HNSW-Vektorindex genutzt, um den Suchraum performant einzugrenzen.

* **Gesamtzahl Patienten:** 916
* **Mögliche Kombinationen (Suchraum):** ca. 419.000 Paare
* **Gefilterte Kandidatenpaare:** 5.927
* **Ausschlussquote:** ~98,5 % der Datensätze wurden erfolgreich als irrelevante Paarungen vorab aussortiert.

**Beobachtung:** Die Cosine-Distanz der Top-Treffer ist extrem gering (z. B. `0.0009`), was auf eine sehr hohe strukturelle und semantische Ähnlichkeit der gefilterten Vektoren hinweist.

---

## 2. Phase: LLM-Judge (Klassifikation)

Die Top-Kandidaten wurden an das lokale Sprachmodell (`qwen2.5:7b`) übergeben. Das Modell wurde angewiesen, als präziser Daten-Analyst zu agieren und das Urteil in ein striktes Pydantic-Schema zu gießen.

### 🟢 Bestätigte Dubletten (High Confidence)

Bei diesen Paaren war sich die KI extrem sicher, dass es sich um dieselbe reale Entität handelt.

* **Paar 4392 (Sicherheit: 95.0% | Signal: ADDRESS)**
  * **Urteil:** Echte Dublette.
  * **Begründung der KI:** Alle Kernfelder (Name, Adresse, Kontaktdaten) sind identisch. Der einzige Unterschied ist das Erfassungsdatum, was auf zwei getrennte Systembuchungen zu verschiedenen Zeitpunkten hindeutet.
* **Paar 4382 (Sicherheit: 95.0% | Signal: NAME)**
  * **Urteil:** Echte Dublette.
  * **Begründung der KI:** Identische Daten. Das Modell hat erfolgreich erkannt, dass der Unterschied bei der Straße (`sonnenwall` vs. `Sonnenwall`) lediglich eine abweichende Schreibweise/Tippfehler (Casing) darstellt.

### 🔴 Keine Dubletten (Human-in-the-Loop Triggered)

Bei diesen Paaren griff der eingestellte Schwellenwert für Unsicherheit (`Confidence < 80%`). Das Modell erkannte starke Ähnlichkeiten, identifizierte aber logische Widersprüche.

* **Paar 5890 (Sicherheit: 60.0% | Signal: ADDRESS)**
  * **Urteil:** Wahrscheinlich keine Dublette (Review nötig).
  * **Begründung der KI:** Besitzer (Herr Minka) und Adresse sind komplett identisch, ebenso die Tierart (Katze). **Aber:** Das Geburtsdatum weicht stark ab (2021 vs. 2024). Das Modell schlussfolgert logisch, dass es sich vermutlich um zwei verschiedene Katzen desselben Besitzers handelt.
* **Paare 4525 & 5208 (Sicherheit: 60.0% | Signal: NAME)**
  * **Urteil:** Wahrscheinlich keine Dublette.
  * **Begründung der KI:** Die Vektoren waren sich aufgrund identischer Namen und Tierarten ähnlich. Die KI erkannte jedoch, dass wesentliche Kontaktdaten (Telefon, E-Mail, Straße) oder das Geburtsdatum völlig unterschiedlich sind.
* **Paar 3245 (Sicherheit: 70.0% | Signal: ADDRESS)**
  * **Urteil:** Wahrscheinlich keine Dublette.
  * **Begründung der KI:** Identischer Name (Paul Frank). Die KI erkannte jedoch, dass es sich um unterschiedliche Postleitzahlen und vor allem unterschiedliche Ortsteile (`Wetzlar-Buederbach` vs. `Wetzlar-Niedergirmes`) handelt, gepaart mit unterschiedlichen Kontaktdaten.

---

## 3. Fazit und Architektur-Bewertung

1. **Robustheit gegen Formatierungsfehler:** Der LLM-Ansatz bewältigt Casing-Fehler (Groß-/Kleinschreibung) und Tippfehler in Adressen fehlerfrei, ohne dass dafür komplexe Regex-Regeln geschrieben werden mussten.
2. **Logisches Schlussfolgern (Reasoning):** Das Modell entscheidet nicht rein nach Zeichen-Überschneidungen (wie Jaro-Winkler), sondern versteht den *Kontext*. Der Fall "gleicher Besitzer, aber anderes Tier-Geburtsdatum" beweist die semantische Stärke der Pipeline.
3. **Schwellenwerte (Confidence):** Die Vorgabe des Pydantic-Schemas zwingt das Modell, eine Wahrscheinlichkeit anzugeben. Werte zwischen 60 % und 70 % eignen sich hervorragend, um die unklaren Fälle automatisch in eine "Human-in-the-Loop"-Warteschlange für manuelle Prüfungen auszuleiten.
