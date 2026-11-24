# Datenqualitätsbericht

Automatisch erzeugt durch `python -m src.run_all`. Rohdaten wurden nicht verändert.

## 1. Ergebnis je Quelle

| Quelle | Geprüfte Werte | Befunde | Vollständig nutzbar % | Befunde je Regel (Anzahl) |
|---|---|---|---|---|
| Q1 | 932 | 6 | 100,0 | DQ07 (3), DQ11 (1), DQ12 (2) |
| Q2 | 1530 | 60 | 100,0 | DQ04 (54), DQ08 (6) |
| Q3 | 1440 | 100 | 100,0 | DQ03 (8), DQ04 (90), DQ09 (1), DQ11 (1) |
| Q4 | 12 | 3 | 100,0 | DQ07 (2), DQ08 (1) |
| SIM | 5810 | 202 | 97,9 | DQ01 (30), DQ02 (25), DQ03 (15), DQ04 (40), DQ05 (15), DQ06 (10), DQ07 (15), DQ08 (40), DQ09 (10), DQ11 (2) |

„Vollständig nutzbar“ heißt: in die Datenbank übernommen. Bei realen Quellen bleibt der Wert auch dann erhalten,
wenn nur sein Standardfehler verworfen wurde. Befunde können mehrere Werte zusammenfassen.

## 2. Qualitätsregeln

| Regel | Prüfart | Beschreibung | Schweregrad | Befunde real | Befunde simuliert |
|---|---|---|---|---|---|
| DQ01 | Fehlende Werte | Ein Ergebniswert ist leer. | Fehler | 0 | 30 |
| DQ02 | Duplikate | Derselbe Schlüssel kommt mehrfach vor (exakt oder widersprüchlich). | Fehler | 0 | 25 |
| DQ03 | Ungültige Wertebereiche | Punkte außerhalb 0 bis Maximum, Prozent außerhalb 0 bis 100, negativer Standardfehler. | Fehler | 8 | 15 |
| DQ04 | Inkonsistente Bezeichnungen | Land oder Schulart weicht von der Referenzliste ab. | Warnung | 144 | 40 |
| DQ05 | Fehlerhafte Datumsangaben | Datum ungültig oder außerhalb des Erhebungsfensters. | Fehler | 0 | 15 |
| DQ06 | Fehlende Identifikatoren | Kind-, Schul- oder Fundstellenangabe fehlt. | Fehler | 0 | 10 |
| DQ07 | Unplausible Kombinationen | Kombination widerspricht der Regel, kann aber eine belegte Ausnahme sein. | Warnung | 5 | 15 |
| DQ08 | Unterschiedliche Datenformate | Zahl oder Datum in abweichender Schreibweise, eindeutig umwandelbar. | Hinweis | 7 | 40 |
| DQ09 | Fehlende Metadaten | Lizenz, Maximalpunktzahl oder Kompetenzbereich fehlt. | Warnung | 1 | 10 |
| DQ10 | Quellenabgleich | Zwei amtliche Quellen widersprechen sich. | Fehler | 0 | 0 |
| DQ11 | Vollständigkeit | Eine erwartete Einheit ist nicht enthalten. | Warnung | 2 | 2 |
| DQ12 | Grundgesamtheit | Gleich benannte Kennzahl meint verschiedene Grundgesamtheiten. | Warnung | 2 | 0 |

## 3. Befunde in den realen Quellen

| Regel | Quelle | Fundstelle | Rohwert | Befund | Behandlung |
|---|---|---|---|---|---|
| DQ03 | Q3 | Q3 / Tab. 4.4web / R22 und 1 weitere | -1.6 | Negativer Standardfehler ist rechnerisch unmöglich | Standardfehler verworfen, Wert bleibt; Vorzeichen wird nicht geraten |
| DQ03 | Q3 | Q3 / Tab. 4.4web / Y22 und 1 weitere | -2.4 | Negativer Standardfehler ist rechnerisch unmöglich | Standardfehler verworfen, Wert bleibt; Vorzeichen wird nicht geraten |
| DQ03 | Q3 | Q3 / Tab. 4.5web / R22 und 1 weitere | -1.5 | Negativer Standardfehler ist rechnerisch unmöglich | Standardfehler verworfen, Wert bleibt; Vorzeichen wird nicht geraten |
| DQ03 | Q3 | Q3 / Tab. 4.6web / R22 | -1.7 | Negativer Standardfehler ist rechnerisch unmöglich | Standardfehler verworfen, Wert bleibt; Vorzeichen wird nicht geraten |
| DQ03 | Q3 | Q3 / Tab. 4.8web / N22 | -0.9 | Negativer Standardfehler ist rechnerisch unmöglich | Standardfehler verworfen, Wert bleibt; Vorzeichen wird nicht geraten |
| DQ04 | Q2 | Q2 / Tab. 4.1web / AD14 und 53 weitere | Mecklenburg-Vormpommern | Schreibweise weicht ab, gemeint: Mecklenburg-Vorpommern | über dokumentierte Aliasliste zugeordnet, Rohwert erhalten |
| DQ04 | Q3 | Q3 / Tab. 3.13web / C28 und 89 weitere | Niedersachen | Schreibweise weicht ab, gemeint: Niedersachsen | über dokumentierte Aliasliste zugeordnet, Rohwert erhalten |
| DQ07 | Q1 | Q1 / csv-21111-04 / I9839 und 1 weitere | 689 | Gymnasium umfasst laut Q4 die Jahrgänge 7 bis 12, hier Klasse 5 | Wert bleibt gültig, Ausnahme fachlich klären |
| DQ07 | Q1 | Q1 / csv-21111-04 / I9848 | 662 | Gymnasium umfasst laut Q4 die Jahrgänge 7 bis 12, hier Klasse 6 | Wert bleibt gültig, Ausnahme fachlich klären |
| DQ07 | Q4 | Q4 / Tabelle 1.9, S. 18 / Jg. 5, Wertspalte 4 | 689 | Gymnasium umfasst laut Q4 die Jahrgänge 7 bis 12, hier Klasse 5 | Wert bleibt gültig, Ausnahme fachlich klären |
| DQ07 | Q4 | Q4 / Tabelle 1.9, S. 18 / Jg. 6, Wertspalte 4 | 662 | Gymnasium umfasst laut Q4 die Jahrgänge 7 bis 12, hier Klasse 6 | Wert bleibt gültig, Ausnahme fachlich klären |
| DQ08 | Q2 | Q2 / Tab. 3.25web | 7.3999999999999995 | 92 Werte mit Gleitkommaresten | auf 6 Nachkommastellen gerundet, Rohwert erhalten |
| DQ08 | Q2 | Q2 / Tab. 3.26web | 3.3000000000000003 | 53 Werte mit Gleitkommaresten | auf 6 Nachkommastellen gerundet, Rohwert erhalten |
| DQ08 | Q2 | Q2 / Tab. 3.27web | 3.5000000000000004 | 63 Werte mit Gleitkommaresten | auf 6 Nachkommastellen gerundet, Rohwert erhalten |
| DQ08 | Q2 | Q2 / Tab. 3.28web | 8.200000000000001 | 71 Werte mit Gleitkommaresten | auf 6 Nachkommastellen gerundet, Rohwert erhalten |
| DQ08 | Q2 | Q2 / Tab. 3.29web | 31.900000000000002 | 77 Werte mit Gleitkommaresten | auf 6 Nachkommastellen gerundet, Rohwert erhalten |
| DQ08 | Q2 | Q2 / Tab. 3.30web | 5.8999999999999995 | 59 Werte mit Gleitkommaresten | auf 6 Nachkommastellen gerundet, Rohwert erhalten |
| DQ08 | Q4 | Q4 / Tabelle 1.9, S. 18 | 15.248 | 6 Werte mit deutschem Tausenderpunkt (15.248 bedeutet 15248) | nach Zahlenvertrag der Quelle umgewandelt |
| DQ09 | Q3 | Q3 | keine Angabe gefunden | Keine Lizenzangabe gefunden | Rohdatei wird nicht weitergegeben, Klärung mit Herausgeber |
| DQ11 | Q1 | csv-21111-07, Klasse 6 | 14543 / 13881 | Schularten ergeben 662 weniger als Insgesamt; vorhanden: Gesamtschule, Regionale Schule | Summenzeile der Quelle verwendet, fehlende Zeile nicht ergänzt |
| DQ11 | Q3 | Q3 |  | Mecklenburg-Vorpommern hat keine Ergebniszeilen | als 'nicht ausgewiesen' mit Grund geführt, kein Ersatzwert |
| DQ12 | Q1 | Klasse 5, Tabellen 04 und 07 | 15248 / 14539 | Differenz entspricht genau Förder- und Waldorfschulen | Verfahren getrennt geführt, Vergleich gesperrt (S6) |
| DQ12 | Q1 | Klasse 6, Tabellen 04 und 07 | 15330 / 14543 | Differenz entspricht genau Förder- und Waldorfschulen | Verfahren getrennt geführt, Vergleich gesperrt (S6) |

## 4. Abgleich zweier amtlicher Quellen (Regel DQ10)

Schülerzahlen in Mecklenburg-Vorpommern, Schuljahr 2025/26. 12 von 12 Werten
stimmen überein.

| Klasse | Schulart | Destatis | Stat. Amt M-V | stimmt überein |
|---|---|---|---|---|
| 5 | Förderschule | 565 | 565 | ja |
| 5 | Gesamtschule | 1698 | 1698 | ja |
| 5 | Gymnasium | 689 | 689 | ja |
| 5 | Insgesamt | 15248 | 15248 | ja |
| 5 | Regionale Schule | 12152 | 12152 | ja |
| 5 | Waldorfschule | 144 | 144 | ja |
| 6 | Förderschule | 669 | 669 | ja |
| 6 | Gesamtschule | 1658 | 1658 | ja |
| 6 | Gymnasium | 662 | 662 | ja |
| 6 | Insgesamt | 15330 | 15330 | ja |
| 6 | Regionale Schule | 12223 | 12223 | ja |
| 6 | Waldorfschule | 118 | 118 | ja |

## 5. Simulierte Daten: Werden eingebaute Fehler erkannt?

In 5810 Rohzeilen wurden 200 Fehlerstellen eingebaut. 5690 Zeilen sind auswertbar,
120 bleiben ausgeschlossen, aber in der Rohdatei erhalten.

| Regel | eingebaut | erkannt | übersehen | fehlalarm |
|---|---|---|---|---|
| DQ01 | 30 | 30 | 0 | 0 |
| DQ02 | 25 | 25 | 0 | 0 |
| DQ03 | 15 | 15 | 0 | 0 |
| DQ04 | 40 | 40 | 0 | 0 |
| DQ05 | 15 | 15 | 0 | 0 |
| DQ06 | 10 | 10 | 0 | 0 |
| DQ07 | 15 | 15 | 0 | 0 |
| DQ08 | 40 | 40 | 0 | 0 |
| DQ09 | 10 | 10 | 0 | 0 |

**Einordnung:** Fehler und Regeln stammen vom selben Team. Eine vollständige Erkennung belegt, dass die Regeln wie
beschrieben arbeiten. Sie belegt nicht, dass unbekannte Fehler in echten Daten gefunden würden.

## 6. Vergleichbarkeit

| Regel | Verfahren A | Verfahren B | Kennzahl | Dimension | Status | Begründung |
|---|---|---|---|---|---|---|
| F1 | V_DESTATIS_SCHUELER | V_STATAMT_MV | schueler_anzahl | quelle | freigegeben | Gleiches Schuljahr, gleiche Grundgesamtheit. Dient nur als Plausibilitätsabgleich. |
| F2 | V_IQB24_KL9_ALLE | V_IQB24_KL9_ALLE | mittelwert | zeit | freigegeben | Das IQB weist diese Trends selbst aus. Differenzen und Standardfehler werden aus der Quelle übernommen, nicht neu berechnet. |
| F3 | V_IQB24_KL9_ALLE | V_IQB24_KL9_ALLE | mittelwert | land | freigegeben | Vergleich mit Deutschland im selben Jahr, Test und Kompetenzbereich ist Zweck der Studie. Kein Ranking. |
| F4 | V_IQB24_KL9_ZIELGLEICH | V_IQB24_KL9_ZIELGLEICH | ms_msa_verfehlt | land | freigegeben | Wie F3, für den Anteil unter dem Mindeststandard. |
| F5 | V_IQB24_KL9_ZIELGLEICH | V_IQB24_KL9_ZIELGLEICH | ms_msa_verfehlt | zeit | freigegeben | Wie F2, für den Anteil unter dem Mindeststandard. |
| F6 | V_SIM_MATHE_OS | V_SIM_MATHE_OS | loesungsanteil | zeit | freigegeben | Beide Messzeitpunkte nutzen per Konstruktion dasselbe fiktive Instrument, gepaart je Kind. |
| F7 | V_SIM_MATHE_OS | V_SIM_MATHE_OS | loesungsanteil | gruppe | freigegeben | Alle Gruppen bearbeiten per Konstruktion dieselben Aufgaben. Beschreibend, nicht kausal, Mindestgröße 10. |
| S1 | V_IQB21_KL4 | V_IQB24_KL9_ALLE | * | quelle | gesperrt | Klasse 4 und Klasse 9: andere Kohorten, Tests und Skalen. Kein Lernverlauf ableitbar. |
| S2 | V_IQB21_KL4 | V_IQB24_KL9_ZIELGLEICH | * | quelle | gesperrt | Wie S1. |
| S3 | V_SIM_MATHE_OS | V_IQB24_KL9_ALLE | * | quelle | gesperrt | Simulierte Werte dürfen nie mit realen Ergebnissen verglichen werden. |
| S4 | V_SIM_MATHE_OS | V_IQB24_KL9_ZIELGLEICH | * | quelle | gesperrt | Wie S3. |
| S5 | V_SIM_MATHE_OS | V_IQB21_KL4 | * | quelle | gesperrt | Wie S3. |
| S6 | V_DESTATIS_SCHUELER | V_DESTATIS_WIEDERHOLER | schueler_anzahl | quelle | gesperrt | Verschiedene Grundgesamtheiten: Die Wiederholertabelle enthält für M-V keine Förder- und Waldorfschulen. |
| S7 | V_IQB24_KL9_ALLE | V_IQB24_KL9_ZIELGLEICH | * | quelle | gesperrt | Alle Neuntklässler gegenüber nur zielgleich Unterrichteten: verschiedene Grundgesamtheiten. |

Bewusst versuchte unzulässige Vergleiche:

- **IQB Klasse 4 gegen IQB Klasse 9:** S1 gesperrt: Klasse 4 und Klasse 9: andere Kohorten, Tests und Skalen. Kein Lernverlauf ableitbar.
- **Simulation gegen IQB Klasse 9:** S3 gesperrt: Simulierte Werte dürfen nie mit realen Ergebnissen verglichen werden.
- **Schülerzahl Tabelle 04 gegen Tabelle 07:** S6 gesperrt: Verschiedene Grundgesamtheiten: Die Wiederholertabelle enthält für M-V keine Förder- und Waldorfschulen.
- **Klassenzahl im Ländervergleich (nicht beantragt):** Keine Regel für V_DESTATIS_KLASSEN und V_DESTATIS_KLASSEN (klassen_anzahl, land). Ohne begründete Freigabe gilt: nicht vergleichbar.
