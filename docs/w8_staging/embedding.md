

### KI-EMBEDDINGS 

### Prozess-Zusammenfassung: KI-Embedding & Vektor-Indizierung

Um Dubletten über verschiedene Praxissysteme hinweg identifizieren zu können, wurden die harmonisierten Kundendaten in hochdimensionale Vektoren (Embeddings) transformiert. Hierzu wurde das Modell `nomic-embed-text` lokal via Ollama eingesetzt, um eine semantische Repräsentation der Kundendaten zu erzeugen.

#### Prozess-Statistik

| Metrik | Wert |
| --- | --- |
| **Harmonisierte Datensätze** | 916 |
| **Modell** | `nomic-embed-text` |
| **Berechnungszeit (lokal)** | 350.8 s |
| **Vektor-Dimensionen** | 768 |
| **Indizierungsmethode** | HNSW (Hierarchical Navigable Small World) |
| **Distanz-Metrik** | Kosinus-Ähnlichkeit |

---

### Inhalt der Tabelle: `transform.kunden_embeddings` (Top 5)
*(Gesamt: 916 indizierte Vektoren, 768 Dimensionen pro Vektor)*

| praxis_id | quell_id | quell_text | embedding |
|---|---|---|---|
| 1 | 1 | Thomas Berger \| Hauptstr. 12 \| 35500 Juckstadt \| +4964501234 \| berger@email.de | [-0.52333647, 0.07747042, -3.9414542, ...] |
| 1 | 2 | Marion Hoffmann \| Kirchgasse 4 \| 35500 Juckstadt \| +4964502233 \| hoffmann@email.de | [-0.3407184, -0.18856432, -3.7923548, ...] |
| 1 | 3 | Klaus Weber \| Am Markt 3 \| 35500 Juckstadt \| +4964509012 | [-0.415011, -0.005448165, -3.8595126, ...] |
| 1 | 4 | Thomas Neumann \| Feldweg 22 \| 35501 Oberstadt \| +4964515588 \| neumann@email.de | [-0.6246771, -0.089225754, -3.8689919, ...] |
| 1 | 5 | Markus Lehmann \| Schulstr. 21 \| 35501 Oberstadt \| +4964517890 | [-0.12201178, -0.79859114, -3.4372346, ...] |
---

### Methodische Anmerkungen

* **Strukturierung:** Die Texte wurden vor dem Embedding nach dem Schema `Name | Adresse | PLZ/Ort | Telefon` strukturiert, um der KI eine klare Gewichtung der Identitätsmerkmale zu ermöglichen.
* **Performance:** Durch die lokale Ausführung von `nomic-embed-text` konnte die Privatsphäre der Patientendaten gewahrt bleiben, während gleichzeitig eine performante Indizierung der 916 Datensätze in unter 6 Minuten erreicht wurde.
* **Validierung:** Die Vektoren umfassen konsistent **768 Dimensionen**, was eine präzise mathematische Vergleichbarkeit im 768-dimensionalen Raum über die Kosinus-Metrik ermöglicht.

**Erfolgs-Check:** Die Vektoren sind erfolgreich indiziert und bilden die mathematische Basis für den nachfolgenden Matching-Prozess (Kandidatensuche).
