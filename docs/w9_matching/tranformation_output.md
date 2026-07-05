## TABELLENINHALTE AUSGEBEN (TRANSFORMATION)

### Inhalt der Tabelle: `transform.norm_kunde`

*(916 Zeilen)*

| kunde_id | praxis_id | quell_id | anrede | vorname | nachname | strasse | plz | ort | telefon_e164 | email | erfasst_am | cluster_id |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | 1 | Herr | Thomas | Berger | Hauptstr. 12 | 35500 | Juckstadt | +4964501234 | berger@email.de | 2021-05-12 | `<NA>` |
| 2 | 1 | 2 | Frau | Marion | Hoffmann | Kirchgasse 4 | 35500 | Juckstadt | +4964502233 | hoffmann@email.de | 2024-11-29 | `<NA>` |
| 3 | 1 | 3 | Herr | Klaus | Weber | Am Markt 3 | 35500 | Juckstadt | +4964509012 | None | 2024-09-29 | `<NA>` |
| 4 | 1 | 4 | Herr | Thomas | Neumann | Feldweg 22 | 35501 | Oberstadt | +4964515588 | neumann@email.de | 2023-04-08 | `<NA>` |
| 5 | 1 | 5 | Herr | Markus | Lehmann | Schulstr. 21 | 35501 | Oberstadt | +4964517890 | None | 2022-03-29 | `<NA>` |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| 912 | 4 | P-4228 | Herr | Xenia | Neumann | Pfarrgasse 10 | 35579 | Wetzlar-Niedergirmes | +49645060825 | None | 2023-06-20 | `<NA>` |
| 913 | 4 | P-4229 | Herr | X. | Neumann | Pfarrgasse 10 | 35579 | Wetzlar-Niedergirmes | +49645060825 | None | 2025-02-22 | `<NA>` |
| 914 | 4 | P-4230 | Herr | Igor | Meyer | Goethestr. 33 | 35579 | Wetzlar-Niedergirmes | +4964502369 | meyer.i@web.de | 2024-06-01 | `<NA>` |
| 915 | 4 | P-4231 | Herr | Nora | Neumann | Wiesenweg 96 | 35579 | Wetzlar-Niedergirmes | +49645006604 | neumann.n@web.de | 2025-07-07 | `<NA>` |
| 916 | 4 | P-4232 | Herr | Yannick | Weber | Schillerstr. 99 | 35580 | Wetzlar-Buederbach | +496450022511 | weber.y@t-online.de | 2024-08-03 | `<NA>` |

---

### Inhalt der Tabelle: `transform.norm_behandlung`

*(600 Zeilen)*

| behandlung_id | praxis_id | quell_id | kunden_id | datum | tier_name | tierart | diagnose | betrag_eur |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | 1 | Krueger | 2026-02-06 | Pumba | None | Augenuntersuchung | 191.17 |
| 2 | 1 | 2 | Lange | 2026-03-04 | Lucky | None | Jaehrliche Impfung | 74.12 |
| 3 | 1 | 3 | Krueger | 2025-11-02 | Lucky | None | Verbandwechsel | 38.26 |
| 4 | 1 | 4 | Stein | 2025-09-11 | Mimi | None | Floehe Behandlung | 152.88 |
| 5 | 1 | 5 | Schmidt | 2026-03-30 | Bello | None | Tumorabklaerung | 167.99 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |
| 596 | 4 | 146 | P-4100 | 2026-01-30 | Luna | Hund | Kontrolle | 146.46 |
| 597 | 4 | 147 | P-4187 | 2026-03-10 | Luna | Hund | Augenuntersuchung | 19.42 |
| 598 | 4 | 148 | P-4057 | 2025-09-29 | Luna | Hund | Ultraschall | 79.08 |
| 599 | 4 | 149 | P-4154 | 2025-11-01 | Luna | Hund | Allergietest | 165.29 |
| 600 | 4 | 150 | P-4061 | 2025-10-16 | Luna | Hund | Ohrenentzuendung | 68.82 |

---

### Hinweis zur Transformation

Die Daten wurden in diesem Schritt erfolgreich standardisiert:

* **Formatierung:** Telefonnummern wurden in das internationale E.164-Format überführt.
* **Typisierung:** Datumsfelder und Beträge wurden in einheitliche SQL-Datentypen konvertiert.
* **Konsolidierung:** Alle 916 Kunden und 600 Behandlungen liegen nun in einer einheitlichen Struktur vor, die als Basis für die nachfolgende Cluster-Analyse dient.
