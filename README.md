Markdown
# Projekt: VetKliniken-Verbund Hessen (Team Zorro)

Dieses Repository enthält die Projektergebnisse für das Modul **Data & Process Integration** des Teams Zorro. 

**Projektziel:** Konsolidierung und Harmonisierung heterogener Tierklinik-Daten (CSV, JSON, XML) in ein einheitliches relationales Zielschema. Besonderer Fokus liegt auf der Entwicklung einer innovativen, KI-gestützten *Entity Resolution Pipeline* (mittels lokaler LLMs und Vector-Search) zur Dublettenerkennung.

## 👤 Projektbeteiligte
* **Jenisa Sivagnanalingham** (Matrikelnr. 1121105) – Solo-Entwicklung, 100% Beitrag

## 🛠️ Technologie-Stack
* **Datenbank:** DuckDB (inkl. VSS-Extension für HNSW-Vektorindizes)
* **KI / Local LLM:** Ollama (Modelle: `nomic-embed-text` für Embeddings, `qwen2.5:7b` als LLM-Judge)
* **Python-Ökosystem:** Pandas, Pydantic (für strukturierten JSON-Output), DuckDB, Requests

## 📁 Repository-Struktur
```text
dpi-tierarztpraxen-team-zorro/
├── docs/
│   ├── w7_profiling/    # Profiling-Reports, Data Dictionary, Fehlerliste
│   └── w8_staging/      # Zeilenstatisk (Überprüfung des Staging-Prozessess), staging_output.md (Tabellenvorschau), ki_sondierung_UPDATE.md, embedding.md, vector_search_output.md
│   └── w9_matching/     # tranformation_output.md, Testprotokoll, PDF-Zwischenbericht, Video-Demo (alt), Testdurchlauf: Protokoll.md,
│   └── w10_golden_record/     # Konsolidierung.md, cluster_results.md, F1_Score.md
│   └── w11_dokumentation/     # DPI_Zorro_Dokumentation.pdf
│   └── w12_final/     # DPI_Zorro_Ergebnis_Reflexion.pdf
├── src/                 # Python-Skripte für ETL und KI-Matching
├── data/                # lokale Quelldaten
├── requirements.txt     # Python-Abhängigkeiten
├── verbund.duckdb    
└── README.md            # Diese Datei

Setup & Installation
Um die Pipeline lokal und datenschutzkonform (ohne externe Cloud-APIs) auszuführen, müssen folgende Voraussetzungen erfüllt sein:

1. Ollama (KI-Server) installieren und Modelle laden:

Bash
ollama pull nomic-embed-text
ollama pull qwen2.5:7b
2. Python-Abhängigkeiten installieren:

Bash
pip install -r requirements.txt

Ausführung der Pipeline
Die Python-Skripte im Ordner src/ bilden die chronologische Daten-Pipeline und müssen in folgender Reihenfolge ausgeführt werden:

python src/01_staging.py — Einlesen der heterogenen Rohdaten in die Staging-Area der DuckDB.

python src/02_transformation.py — Harmonisierung und Strukturierung der Daten.

python src/03_embedding.py — Semantische Vektorisierung der Kundendaten.

python src/04_vector_search.py — Performante Suchraumreduktion durch Nächste-Nachbarn-Suche.

python src/05_llm_judge.py — KI-Bewertung der Dubletten-Kandidaten (strukturiert via Pydantic).

python src/06_golden_record_load.py — Finale Konsolidierung und Beladung des Zielschemas.
```

## Wichtigste Projektergebnisse
Durch den Einsatz der KI-gestützten Entity-Resolution-Pipeline konnte eine **Precision von 100%** bei der Dublettenerkennung erreicht werden. Dies garantiert eine fehlerfreie Konsolidierung der Patientendaten, was essenziell für die medizinische Datenintegrität in einem Klinikverbund ist.

## Projektergebnisse & Evaluation

### Endergebnis der Datenintegration
Durch die KI-gestützte Dublettenerkennung (Embeddings + LLM-Judge) konnten redundante Kundendatensätze erfolgreich konsolidiert werden. Alle Behandlungen wurden anschließend durch fehlertolerante Joins verlustfrei den entsprechenden Golden Records zugeordnet und in das finale Zielmodell übernommen.

| Kennzahl | Wert |
| :--- | :--- |
| **Ursprüngliche Kundendatensätze** | 916 |
| **Konsolidierte Golden Records** | 893 |
| **Zugeordnete Behandlungen** | 600 |

### Evaluation der Matching-Güte
Die Qualität des LLM-basierten Matchings (`qwen2.5:7b-instruct`) wurde gegen einen manuell kuratierten Goldstandard evaluiert.

*Hinweis: Zur Schonung lokaler Hardwareressourcen wurde der Evaluierungs-Durchlauf für diesen Proof of Concept künstlich auf die Top 30 Kandidatenpaare limitiert.*

| Metrik | Wert |
| :--- | :--- |
| True Positives | 24 |
| False Positives | 0 |
| False Negatives | 120* |
| **Precision** | **1.0000 (100 %)** |
| **Recall** | 0.1667 (16,67 %)*|
| **F1-Score** | 0.2857 (28,57 %)|

*\*Die False Negatives und der daraus resultierende niedrige Recall sind direkte Artefakte der Limitierung auf 30 LLM-Aufrufe und spiegeln nicht das Erkennungslimit der KI wider.*
