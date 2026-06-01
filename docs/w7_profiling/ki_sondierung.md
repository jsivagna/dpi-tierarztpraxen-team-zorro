# Sondierung verfügbarer Modelle und Embedding-Qualität (Szenario B)

Für den Meilenstein W7 habe ich die im Projektbrief geforderten KI-Modelle für das Entity-Matching evaluiert. Da ich das Projekt als Solo-Entwickler unter Berücksichtigung begrenzter Zeitressourcen sowie Hardware-Umgebungen (MacBook Air 13) durchführe, liegt mein architektonischer Fokus auf maximaler Stabilität, Ausfallsicherheit und minimalem Wartungsaufwand.

Ich habe mich daher gegen lokale Laufzeitumgebungen via Ollama und für einen **"Full-Cloud-Ansatz"** entschieden. Da es sich hier zudem nur um ein erfundendes Szenario handelt und wir keine realen, sensiblen Daten beinhalten, spielt der Faktor Datenschutz in diesem Fall keinen entscheidenen Faktor.

## 1. Embedding-Modell
* **Entscheidung:** Nutzung von `text-embedding-3-small` (via OpenAI API).
* **Begründung:** Ich habe mich bewusst gegen das im Projekt vorgeschlagene `nomic-embed-text` (lokale Ausführung) entschieden, da eine lokale Vektorisierung meiner Daten den Arbeitsspeicher meines MacBook Air überproportional belasten würde. Die Cloud-API `text-embedding-3-small` ist extrem performant, kosteneffizient und liefert hochgradig semantisch trennscharfe Vektoren für die Kunden- und Adressdaten. Dies entlastet meine lokale Hardware vollständig beim Aufbau des DuckDB Vector-Index.

## 2. LLM-Judge (Klassifikation der Dubletten)
Die größte technische Herausforderung ist die strikte Einhaltung des geforderten Pydantic-Schemas (`is_duplicate`, `confidence`, `reasoning`, `decisive_signal`). Lokale Modelle (z.B. Llama-3-8B) neigen unter Ressourcenbeschränkungen gelegentlich zu Formatierungsfehlern im JSON-Output, was aufwendige Retry-Logiken und manuelles Debugging erfordern würde.

* **Strategie:** Einsatz eines leistungsfähigen Cloud-Modells (z.B. `gpt-4o-mini`, `gemini-1.5-flash` oder `claude-3-haiku`).
* **Begründung:** 1. **Zuverlässigkeit:** Diese Cloud-Modelle unterstützen nativ "Structured Outputs". Das Pydantic-Schema wird serverseitig garantiert eingehalten, wodurch ich Parser-Fehler in meiner Pipeline eliminieren kann.
  2. **Ressourcen-Effizienz:** Da das Matching rein über REST-API-Calls stattfindet, ist die Pipeline hardware-unabhängig. Sie läuft stabil auf meinem MacBook Air, da die Rechenlast vollständig in der Cloud liegt.
  3. **Kosteneffizienz:** Durch die vorgeschaltete Vector-Search werden dem LLM nur die 20–30 relevantesten Kandidatenpaare vorgelegt. Die Token-Kosten bewegen sich dadurch im minimalen Cent-Bereich, was den massiven Zeitgewinn bei der Entwicklung rechtfertigt.

## 3. Anbieterwahl (Flexibilität)
Ich habe mich für den Cloud-Ansatz entschieden, halte mir die konkrete Anbieterwahl (OpenAI, Google oder Anthropic) jedoch für den Zeitpunkt der Implementierung in Woche 8 offen. Da ich den LLM-Aufruf durch ein **Interface-Design (Wrapper-Funktion)** vom Rest der Pipeline entkoppelt habe, ist ein Wechsel zwischen den Anbietern jederzeit mit minimalem Anpassungsaufwand möglich. So kann ich nach ersten Testläufen entscheiden, welcher Anbieter die beste Logik (Reasoning) für meine spezifischen Tierarztdaten liefert.

