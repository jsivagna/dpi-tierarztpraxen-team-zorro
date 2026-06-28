## KI-EMBEDDINGS (STAGING-SCHICHT)

Die harmonisierten Kundendaten wurden erfolgreich über das lokale Modell `nomic-embed-text` (via Ollama) in Vektoren übersetzt und in DuckDB mit einem HNSW-Index für schnelle Ähnlichkeitssuchen versehen.

### Inhalt der Tabelle: `staging.kunden_embeddings` (Top 5)
*(Gesamt: 916 indizierte Vektoren, 768 Dimensionen pro Vektor)*

| praxis_id | quell_id | quell_text | embedding |
|---|---|---|---|
| 1 | 1 | Thomas Berger \| Hauptstr. 12 \| 35500 Juckstadt \| +4964501234 \| berger@email.de | [-0.52333647, 0.07747042, -3.9414542, ...] |
| 1 | 2 | Marion Hoffmann \| Kirchgasse 4 \| 35500 Juckstadt \| +4964502233 \| hoffmann@email.de | [-0.3407184, -0.18856432, -3.7923548, ...] |
| 1 | 3 | Klaus Weber \| Am Markt 3 \| 35500 Juckstadt \| +4964509012 | [-0.415011, -0.005448165, -3.8595126, ...] |
| 1 | 4 | Thomas Neumann \| Feldweg 22 \| 35501 Oberstadt \| +4964515588 \| neumann@email.de | [-0.6246771, -0.089225754, -3.8689919, ...] |
| 1 | 5 | Markus Lehmann \| Schulstr. 21 \| 35501 Oberstadt \| +4964517890 | [-0.12201178, -0.79859114, -3.4372346, ...] |

**Validierung:** 
✅ Die Vektoren weisen durchgehend die vom Modell vorgegebene Dimensionalität (768) auf.
✅ Der HNSW-Index (Kosinus-Metrik) wurde zur Beschleunigung der nachfolgenden Vector-Search erfolgreich über die Spalte `embedding` gelegt.
