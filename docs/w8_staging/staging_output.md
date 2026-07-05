## TABELLENINHALTE AUSGEBEN

### Inhalt der Tabelle: `staging.juck_kunden`

*(223 Zeilen)*

| quell_zeile | kunden_nr | anrede | vorname | nachname | strasse | plz | ort | telefon | email | angelegt_am |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | Herr | Thomas | Berger | Hauptstr. 12 | 35500 | Juckstadt | 06450-1234 | berger@email.de | 2021-05-12 |
| 2 | 2 | Frau | Marion | Hoffmann | Kirchgasse 4 | 35500 | Juckstadt | 06450-2233 | hoffmann@email.de | 2024-11-29 |
| 3 | 3 | Herr | Klaus | Weber | Am Markt 3 | 35500 | Juckstadt | 06450-9012 | None | 2024-09-29 |
| 4 | 4 | Herr | Thomas | Neumann | Feldweg 22 | 35501 | Oberstadt | 06451-5588 | neumann@email.de | 2023-04-08 |
| 5 | 5 | Herr | Markus | Lehmann | Schulstr. 21 | 35501 | Oberstadt | 06451-7890 | None | 2022-03-29 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| 219 | 219 | Herr | Bernd | Wagner | Kapellenweg 81 | 35511 | Hoehental | 06450-137810 | wagner.b@t-online.de | 2026-07-02 |
| 220 | 220 | Herr | Xaver | Schmitt | Lindenallee 82 | 35510 | Bergblick-Siedlung | 06450-906967 | schmitt.x@gmx.de | 2026-09-21 |
| 221 | 221 | Herr | Olivia | Schmid | Lindenallee 4 | 35511 | Hoehental | 06450-48829 | schmid.o@web.de | 2026-07-21 |
| 222 | 222 | Herr | B. | Schaefer | Rosenweg 87 | 35511 | Hoehental | 06450-16471 | None | 2023-11-10 |
| 223 | 223 | Herr | Quirin | Kohc | Schillerstr. 58 | 35510 | Waldrand | 06450-2225 | koch.q@gmx.de | 2020-02-06 |

---

### Inhalt der Tabelle: `staging.juck_behandlungen`

*(150 Zeilen)*

| quell_zeile | beh_nr | datum | patient_name | kunde_nachname | diagnose | kosten_euro |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | 2026-02-06 | Pumba | Krueger | Augenuntersuchung | 191,17 |
| 2 | 2 | 2026-03-04 | Lucky | Lange | Jaehrliche Impfung | 74,12 |
| 3 | 3 | 2025-11-02 | Lucky | Krueger | Verbandwechsel | 38,26 |
| 4 | 4 | 2025-09-11 | Mimi | Stein | Floehe Behandlung | 152,88 |
| 5 | 5 | 2026-03-30 | Bello | Schmidt | Tumorabklaerung | 167,99 |
| ... | ... | ... | ... | ... | ... | ... |
| 146 | 146 | 2025-10-11 | Balou | Meyer | Jaehrliche Impfung | 194,85 |
| 147 | 147 | 2025-10-15 | Emma | Schneider | Zahnsteinentfernung | 99,28 |
| 148 | 148 | 2025-12-20 | Nala | Fischer | Zeckenbefall Spot-On | 140,92 |
| 149 | 149 | 2025-11-03 | Lola | Schaefer | Wundversorgung | 127,52 |
| 150 | 150 | 2025-12-18 | Rocky | Schmitt | Wurmkur | 25,92 |

---

### Inhalt der Tabelle: `staging.wald_kunden`

*(227 Zeilen)*

| quell_zeile | customer_id | first_name | last_name | street | zip_code | city | phone | email_address | created_at | marketing_consent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | W-1001 | Thomas | Berger | Hauptstr. 12 | 35500 | Juckstadt | +49 645 01234 | berger@email.de | 02/09/2022 |  |
| 2 | W-1002 | K. | None | Am Markt 3 | 35500 | Juckstadt | 0645 09012 | weber@email.de | 05/29/2025 | True |
| 3 | W-1003 | Petra | Vogel | Eichenallee 8 | 35466 | Rabenau | 0640/777991 | None | 12/29/2024 | False |
| 4 | W-1004 | Bernd | Schulz | Dorfstr. 44 | 35466 | Rabenau | 0640 7771212 | schulz@email.de | 11/21/2021 |  |
| 5 | W-1005 | Frank | Neumann | Feldweg 22 | 35501 | Oberstadt | 0645 15588 | neumann@email.de | 10/14/2023 | False |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| 223 | W-1223 | V. | Schaefer | Parkstr. 15 | 35511 | Hoehental | +49 645 0678682 | None | 05/02/2021 | True |
| 224 | W-1224 | Verena | Kohc | Rosenweg 63 | 35510 | Waldrand | 0645/0546363 | koch.v@gmx.de | 10/24/2022 |  |
| 225 | W-1225 | Ines | Pteers | Feldweg 98 | 35511 | Hoehental | 0645 0727981 | peters.i@email.de | 08/20/2019 | True |
| 226 | W-1226 | Katrin | Wagenr | Hauptstrasse 54 | 35510 | Bergblick-Siedlung | 0645/0011706 | wagner.k@t-online.de | 05/12/2021 |  |
| 227 | W-1227 | Diana | Braun | Sonnenwall 94 | 35510 | Bergblick-Siedlung | +49 645 03657 | braun.d@email.de | 10/28/2025 |  |

---

### Inhalt der Tabelle: `staging.wald_behandlungen`

*(150 Zeilen)*

| quell_zeile | treatment_id | customer_id | animal_name | species | treatment_date | diagnosis | total_eur |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | T20250151 | W-1067 | Smokey | cat | 2025-12-11 | Flea treatment | 199.85 |
| 2 | T20250152 | W-1210 | Kitty | cat | 2026-01-17 | Flea treatment | 59.78 |
| 3 | T20250153 | W-1013 | Felix | cat | 2026-03-22 | Ultrasound | 35.02 |
| 4 | T20250154 | W-1024 | Pumba | cat | 2025-10-02 | Flea/tick treatment | 37.98 |
| 5 | T20250155 | W-1015 | Kitty | cat | 2025-10-18 | Check-up | 148.28 |
| ... | ... | ... | ... | ... | ... | ... | ... |
| 146 | T20250296 | W-1101 | Lilly | dog | 2025-09-25 | Follow-up | 147.81 |
| 147 | T20250297 | W-1118 | Daisy | dog | 2026-01-12 | X-ray | 95.28 |
| 148 | T20250298 | W-1151 | Emma | dog | 2026-01-06 | Annual vaccination | 66.95 |
| 149 | T20250299 | W-1225 | Lulu | cat | 2025-12-10 | Check-up | 24.61 |
| 150 | T20250300 | W-1005 | Nala | dog | 2025-12-02 | Flea treatment | 165.50 |

---

### Inhalt der Tabelle: `staging.schm_kunden`

*(234 Zeilen)*

| quell_zeile | nachname | vorname | anrede | plz | ort | strasse | tel | email | erfasst |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Berger | Th. | Hr. | 35500 | Juckstadt | Hauptstr. 12 | 0645 01234 | berger@email.de | 2020-12-06 |
| 2 | Hoffmann | Marion | Fr. | 35500 | Juckstadt | Kirchgasse 4 | 0645 02233 | hoffmann@email.de | 2024-03-02 |
| 3 | Klaus | Weber | Hr. | 35500 | Juckstadt | Am Markt 3 | 0645 09012 | weber@email.de | 2024-02-06 |
| 4 | Vogel | Petra | Fr. | 35466 | Rabenau | Eichenallee 8 | 0640 7779912 | vogel@email.de | 2025-04-25 |
| 5 | Lehmann | M. | Hr. | 35501 | Oberstadt | Schulstr. 21 | 0645 17890 | lehmann@email.de | 2023-08-24 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| 230 | Frank | V. | Hr. | 35511 | Hoehental | Rosenweg 70 | 0645 086700 | frank.v@email.de | 2021-04-22 |
| 231 | Peters | Sabine | Hr. | 35511 | Hoehental | kirchstr. 22 | 0645 059926 | None | 2022-09-16 |
| 232 | Hofmann | P. | Hr. | 35511 | Hoehental | Kirchstr. 80 | 0645 043209 | None | 2024-11-14 |
| 233 | Schneider | Xaver | Hr. | 35510 | Waldrand | Mozartstr. 12 | 0645 000705 | None | 2023-02-11 |
| 234 | Schneider | Claudia | Hr. | 35510 | Waldrand | Sonnenwall 50 | 0645 0431860 | None | 2021-05-03 |

---

### Inhalt der Tabelle: `staging.schm_behandlungen`

*(150 Zeilen)*

| quell_zeile | id | datum | kunde | tier | leistung | betrag |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 301 | 24.09.2025 | Schneider X. | {'name': 'Caesar', 'art': 'Katze'} | Vorsorgeuntersuchung | 15,46 EUR |
| 2 | 302 | 13.10.2025 | Schneider T. | {'name': 'Tiger', 'art': 'Katze'} | Kontrolle | 148,99 EUR |
| 3 | 303 | 24.03.2026 | Muleler I. | {'name': 'Caesar', 'art': 'Katze'} | Vorsorgeuntersuchung | 167,34 EUR |
| 4 | 304 | 10.03.2026 | Klein G. | {'name': 'Ace', 'art': 'Hund'} | Tumorabklaerung | 91,09 EUR |
| 5 | 305 | 06.03.2026 | Lehmann E. | {'name': 'Smokey', 'art': 'Katze'} | Zeckenbefall Spot-On | 52,04 EUR |
| ... | ... | ... | ... | ... | ... | ... |
| 146 | 446 | 07.10.2025 | Becker N. | {'name': 'Tiger', 'art': 'Katze'} | Blutbild | 53,93 EUR |
| 147 | 447 | 28.01.2026 | Hofmann F. | {'name': 'Buddy', 'art': 'Hund'} | Kontrolle | 52,02 EUR |
| 148 | 448 | 07.02.2026 | Mueller S. | {'name': 'Kitty', 'art': 'Katze'} | Augenuntersuchung | 190,55 EUR |
| 149 | 449 | 02.12.2025 | Klein G. | {'name': 'Cleo', 'art': 'Katze'} | Lahmheitsuntersuchung | 85,26 EUR |
| 150 | 450 | 04.12.2025 | Schmitt R. | {'name': 'Rex', 'art': 'Hund'} | Augenuntersuchung | 68,13 EUR |

---

### Inhalt der Tabelle: `staging.berg_patienten`

*(232 Zeilen)*

| quell_zeile | quell_id | erfasst | anrede | name | telefon | email | strasse | plz | ort |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | P-4001 | 2021-06-20 | Herr | Thomas Berger | 0645-01234 | berger@email.de | Hauptstrasse 12 | 35500 | Juckstadt |
| 2 | P-4002 | 2024-04-07 | Frau | Marion Hoffmann | 0645-02233 | hoffmann@email.de | Kirchgasse 4 | 35500 | Juckstadt |
| 3 | P-4003 | 2025-11-23 | Frau | Petra Vogel | 0640-7779913 | vogel@email.de | Eichenallee 8 | 35466 | Rabenau |
| 4 | P-4004 | 2021-02-11 | Herr | B. Schulz | 0640-7771212 | schulz@email.de | Dorfstr. 44 | 35466 | Rabenau |
| 5 | P-4005 | 2022-06-13 | Frau | Bettina Klein | 0645-020031 | klein.b@gmx.de | Bergstr. 9 | 35510 | Waldrand |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| 228 | P-4228 | 2023-06-20 | Herr | Xenia Neumann | 0645-060825 | None | Pfarrgasse 10 | 35579 | Wetzlar-Niedergirmes |
| 229 | P-4229 | 2025-02-22 | Herr | X. Neumann | 0645-060825 | None | Pfarrgasse 10 | 35579 | Wetzlar-Niedergirmes |
| 230 | P-4230 | 2024-06-01 | Herr | Igor Meyer | 0645-02369 | meyer.i@web.de | Goethestr. 33 | 35579 | Wetzlar-Niedergirmes |
| 231 | P-4231 | 2025-07-07 | Herr | Nora Neumann | 0645-006604 | neumann.n@web.de | Wiesenweg 96 | 35579 | Wetzlar-Niedergirmes |
| 232 | P-4232 | 2024-08-03 | Herr | Yannick Weber | 0645-0022511 | weber.y@t-online.de | Schillerstr. 99 | 35580 | Wetzlar-Buederbach |

---

### Inhalt der Tabelle: `staging.berg_behandlungen`

*(150 Zeilen)*

| quell_zeile | patient_id | datum | diagnose | tier_name | tier_art | betrag_netto |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | P-4191 | 2025-11-15 | Tumorabklaerung | Luna | Hund | 162.92 |
| 2 | P-4094 | 2025-11-02 | Zahnsteinentfernung | Luna | Hund | 32.55 |
| 3 | P-4036 | 2026-03-12 | Allergietest | Luna | Hund | 161.95 |
| 4 | P-4026 | 2025-09-22 | Tumorabklaerung | Luna | Hund | 135.18 |
| 5 | P-4085 | 2026-01-22 | Tumorabklaerung | Luna | Hund | 71.45 |
| ... | ... | ... | ... | ... | ... | ... |
| 146 | P-4100 | 2026-01-30 | Kontrolle | Luna | Hund | 146.46 |
| 147 | P-4187 | 2026-03-10 | Augenuntersuchung | Luna | Hund | 19.42 |
| 148 | P-4057 | 2025-09-29 | Ultraschall | Luna | Hund | 79.08 |
| 149 | P-4154 | 2025-11-01 | Allergietest | Luna | Hund | 165.29 |
| 150 | P-4061 | 2025-10-16 | Ohrenentzuendung | Luna | Hund | 68.82 |

---
