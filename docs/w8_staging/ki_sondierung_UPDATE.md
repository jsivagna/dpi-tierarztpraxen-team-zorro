# KI-Sondierung (UPDATE) W8

In meiner Sondierung (W7) hatte ich mich initial für einen Cloud-Ansatz (OpenAI/Google API) entschieden. Jedoch kam es hierbei zu folgendem Hindernis: 
**Rate Limits (Google API):** Beim Versuch, für das Embedding und die Berechnung des Vector-Index mit der Gemini API zu verfahren, stieß die Pipeline beim Batch-Processing von 916 Kunden in der letzten Runde an das `429 RESOURCE_EXHAUSTED` Limit des Free-Tiers.

Aus diesem Grund habe ich mich nun doch entschieden  den vorgeschlagenen lokalen Ansatz via **Ollama** zu verwenden. 
Mit dem Modell `nomic-embed-text` konnten die 916 Kunden-Datensätze erfolgreich in 768-dimensionale Embeddings übersetzt und in den DuckDB-HNSW-Index geladen werden.
