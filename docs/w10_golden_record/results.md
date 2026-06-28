ERGEBNISSE

34 Datensätze wurden erfolgreich in 9 Clustern zusammengefasst.
892 Golden Records (Patienten) erfolgreich erstellt.
150 Behandlungen nahtlos zugeordnet.

Gefundene Dubletten-Paare (LLM) : 130
Echte Dubletten-Paare (Gold)    : 144
--------------------------------------------------
Korrekt gefunden (True Positives)    : 10
Falsch verknüpft (False Positives)   : 120
Übersehen / Nicht erkannt (False Neg.): 134
--------------------------------------------------
🎯 Precision (Genauigkeit) : 7.69%
🎯 Recall (Trefferquote)   : 6.94%
🏆 F1-Score               : 7.30%
==================================================


Ein F1-Score von 7,3% deutet darauf hin, dass die Pipeline zwar "aktiv" ist, aber bei der Verknüpfung der Datensätze systematische Fehler macht. Hier sind die wahrscheinlichsten Ursachen:

A. Prompting-Strategie (LLM-Judge)
"Halluzinierte" Dubletten: Wenn das LLM bei vielen Paaren is_duplicate: true zurückgegeben hat, obwohl sie keine sind (wie die 120 False Positives zeigen), war der Prompt vermutlich zu tolerant (bspw. die lockere Regel bei Telefonnummern & E-Mail-Adressen)

Konfidenz-Threshold: Du hast das LLM nach einer Sicherheit gefragt. Hast du im Code nur is_duplicate == True gefiltert oder auch confidence > 0.9? Wenn du alle LLM-Entscheidungen genommen hast, hast du das "Rauschen" der unsicheren Entscheidungen mit in die Datenbank übernommen.

B. Matching-Logik (Die Ursache der False Positives)
Fehlende "Blocking"-Logik: Zu viele Paare wurden evtl. an das LLM gesendet. Wenn z.B. jeden "Müller" mit jedem "Müller" vergleichst, ohne die PLZ oder Straße als zwingende Bedingung vorauszusetzen, entstehen hunderte falsche Paarungen, von denen das LLM dann einige fälschlicherweise bestätigt.

Transitive Hülle (Cluster-Fehler): Wenn nur ein einziges falsches Paar vom LLM erscheint (z.B. Datensatz A und Datensatz X werden fälschlich als Dubletten markiert), "infiziert" dieser Fehler das gesamte Cluster. Wenn A eigentlich zu Cluster 1 gehört und X zu Cluster 50, werden durch diesen einen Fehler beide Cluster zu einem riesigen, falschen Cluster verschmolzen. Das erklärt die hohe Zahl an False Positives.


Die Pipeline zeigt eine hohe Aktivität beim Matching, jedoch eine geringe Spezifität. Die hohe Anzahl an False Positives deutet darauf hin, dass die Kriterien für das LLM-Judge-Modell zu weit gefasst waren. Insbesondere die Bildung der transitiven Hülle hat dazu geführt, dass sich einzelne Fehlentscheidungen auf ganze Cluster-Gruppen ausgewirkt haben. Für eine Verbesserung wäre eine strengere Filterung (höherer Konfidenz-Score im Prompt) und eine Vorauswahl der Kandidaten durch exakte Übereinstimmung.
