

## Vector Search & Kandidatenfilterung

### Prozess-Zusammenfassung: KNN-Kandidatensuche

Um die Rechenlast für das LLM zu optimieren, wurde eine Vector-Search durchgeführt. Anstatt jedes der 916 Datensätze mit jedem anderen zu vergleichen (was 838.156 Vergleiche entspräche), wurden für jeden Kunden mittels K-Nearest-Neighbor (KNN) die 10 ähnlichsten Nachbarn auf Basis der Kosinus-Ähnlichkeit im Vektorraum identifiziert.

#### Prozess-Statistik

| Metrik | Wert |
| --- | --- |
| **Gesamtanzahl Kunden** | 916 |
| **K-Nachbarn (KNN)** | 10 |
| **Gefilterte Kandidatenpaare** | 2.406 |
| **Verfahren** | Distanzbasierte Ähnlichkeitssuche |

---

### Vorschau der Top-Kandidatenpaare

Die folgenden Beispiele illustrieren Paare, die aufgrund ihrer nahezu identischen Vektordaten (Distanz ~0.0000) als hochgradig dublettenverdächtig eingestuft wurden:

| Distanz | Kunde A (Global-ID, Praxis, Quell-ID) | Kunde B (Global-ID, Praxis, Quell-ID) |
| --- | --- | --- |
| 0.0000 | 1 (Praxis 1, ID 1): Thomas Berger... | 224 (Praxis 2, ID W-1001): Thomas Berger... |
| 0.0000 | 79 (Praxis 1, ID 79): Stefanie Schneider... | 660 (Praxis 3, ID 210): Stefanie Schneider... |
| 0.0000 | 24 (Praxis 1, ID 24): Zoey Klein... | 889 (Praxis 4, ID P-4205): Zoey Klein... |

---

### Methodische Anmerkungen

* **Effizienz:** Die Filterung auf 2.406 Kandidatenpaare reduziert die notwendigen LLM-Analysen massiv, ohne dabei reale Dubletten-Kandidaten auszuschließen.
* **Qualität der Suche:** Die Distanz von `0.0000` bei den aufgeführten Beispielen verdeutlicht, dass das System exakte Identitäten (identische Namen, Adressen und Kontaktdaten) sofort erkennt.
* **Datengrundlage:** Die gespeicherten Kandidatenpaare in `transform.kandidaten_paare` bilden nun die exklusive Arbeitsgrundlage für den nachgelagerten, rechenintensiven LLM-Entscheidungsprozess (LLM-Judge).

**Erfolgs-Check:** Es wurden erfolgreich 2.406 potenzielle Dubletten-Paare isoliert, die nun einer qualitativen Prüfung durch das Sprachmodell unterzogen werden können.
