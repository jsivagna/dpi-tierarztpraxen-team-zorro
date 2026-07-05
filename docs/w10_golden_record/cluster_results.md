### Cluster-Bildung (Transitive Hülle)

### Prozess-Zusammenfassung: Graphenbasierte Konsolidierung

Um Dubletten-Ketten korrekt aufzulösen (z. B. wenn Datensatz A=B und B=C, dann ist A=B=C), wurde der Graph der verifizierten Matches analysiert. Über die Berechnung der **transitiven Hülle** (transitive closure) wurden die einzelnen Verbindungen zu logischen Gruppen ("Clustern") zusammengefasst.

#### Prozess-Statistik

| Metrik | Wert |
| --- | --- |
| **Verifizierte Dubletten-Datensätze** | 45 |
| **Anzahl resultierender Cluster** | 22 |
| **Speicherort des Mappings** | `embeddings.cluster_mapping` |

---

### Funktionsweise der Cluster-Bildung

* **Transitive Hülle:** Durch den Einsatz der Graphentheorie wurde sichergestellt, dass auch indirekte Verbindungen erkannt werden. Alle miteinander verbundenen Datensätze bilden nun eine eindeutige `cluster_id`.
* **Daten-Synthese:** Das resultierende Cluster-Mapping ist der finale Bauplan für die `verbund_kunde` Tabelle. Jedes Cluster repräsentiert einen "Golden Record", in den die Informationen der gruppierten Datensätze konsolidiert werden.

---

### Beispiel für ein Cluster-Mapping

Die folgende Tabelle zeigt beispielhaft, wie die zuvor einzeln identifizierten Dubletten-Paare nun in einem Cluster zusammengeführt wurden:

| Cluster-ID | Praxis-ID | Quell-ID (Referenz) | Status |
| --- | --- | --- | --- |
| 2 | 1 | 2 | Dubletten-Mitglied |
| 2 | 3 | 452 | Dubletten-Mitglied |
| 2 | 3 | 686 | Dubletten-Mitglied |
| 10003 | 1 | 3 | Eindeutiger Datensatz (Singleton) |

---

### Methodische Anmerkungen

* **Stabilität:** Die Bildung von 22 Clustern aus 45 Datensätzen bestätigt eine hohe Dichte an Mehrfach-Dubletten in den Rohdaten, die durch die Graphenanalyse sauber separiert wurden.
* **Vorbereitung:** Dieses Mapping ist das fundamentale Bindeglied für den letzten Schritt: die Erstellung der Golden Records. Die `cluster_id` dient dabei als primärer Anker für die Konsolidierungslogik.

**Erfolgs-Check:** Alle Dubletten wurden erfolgreich in logische Einheiten überführt. Das System ist nun bereit, aus diesen 22 Clustern die finalen, bereinigten Stammdatensätze (Golden Records) zu generieren.

