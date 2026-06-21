Markdown
# Projekt: VetKliniken-Verbund Hessen (Team Zorro)

Dieses Repository enthält die Projektergebnisse für das Modul **Fortgeschrittene Datenintegration / Data Engineering** des Teams Zorro. 

**Projektziel:** Konsolidierung und Harmonisierung heterogener Tierklinik-Daten (CSV, JSON, XML) in ein einheitliches relationales Zielschema. Besonderer Fokus liegt auf der Entwicklung einer innovativen, KI-gestützten *Entity Resolution Pipeline* (mittels lokaler LLMs und Vector-Search) zur fehlerresistenten Dublettenerkennung.

## 👤 Projektbeteiligte
* **Jenisa Sivagnanalingham** (Matrikelnr. 1121105) – Solo-Entwicklung, 100% Beitrag

## 🛠️ Technologie-Stack
* **Datenbank:** DuckDB (inkl. VSS-Extension für HNSW-Vektorindizes)
* **KI / Local LLM:** Ollama (Modelle: `nomic-embed-text` für Embeddings, `qwen2.5:7b` als Judge)
* **Python-Ökosystem:** Pandas, Pydantic (für strukturierten JSON-Output), DuckDB, Requests

## 📁 Repository-Struktur
```text
dpi-tierarztpraxen-team-zorro/
├── docs/
│   ├── w7_profiling/    # Profiling-Reports, Data Dictionary, Fehlerliste
│   └── w9_matching/     # Testprotokoll, PDF-Zwischenbericht, Video-Demo (W9)
├── src/                 # Python-Skripte für ETL und KI-Matching
├── data/                # (Platzhalter) Für die lokalen Quell- und Zieldaten
├── requirements.txt     # Python-Abhängigkeiten
└── README.md            # Diese Datei
🚀 Setup & Installation
Um die Pipeline lokal und datenschutzkonform (ohne externe Cloud-APIs) auszuführen, müssen folgende Voraussetzungen erfüllt sein:

1. Ollama (KI-Server) installieren und Modelle laden:

Bash
ollama pull nomic-embed-text
ollama pull qwen2.5:7b
2. Python-Abhängigkeiten installieren:

Bash
pip install -r requirements.txt
⚙️ Ausführung der Pipeline
Die Python-Skripte im Ordner src/ bilden die chronologische Daten-Pipeline und müssen in folgender Reihenfolge ausgeführt werden:

python src/01_staging.py - Einlesen der heterogenen Rohdaten in die Staging-Area der DuckDB.

python src/02_embeddings.py - Semantische Vektorisierung der Kundendaten.

python src/03_vector_search.py - Performante Suchraumreduktion durch Nächste-Nachbarn-Suche.

python src/04_llm_judge.py - KI-Bewertung der Dubletten-Kandidaten (strukturiert via Pydantic).

python src/05_transform.py - Klassische Datenbereinigung (Datums- & Währungsformate) für das finale relationale Schema.
