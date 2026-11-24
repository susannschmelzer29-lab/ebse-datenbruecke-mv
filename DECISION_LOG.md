# Entscheidungslog

**PL** = Projektleitung (fachliche Entscheidung), **KI** = technische Umsetzung durch den KI-Assistenten.

## Fachliche Entscheidungen der Projektleitung

| Nr. | Datum | Entscheidung | Begründung |
|---|---|---|---|
| PL-1 | 24.11.2026 | Reale Quellen Q1 bis Q4; Schulverzeichnis und Mikrodaten nicht | geprüft und zugänglich; Datenminimierung |
| PL-2 | 24.11.2026 | Indikator: Lösungsanteil je Leitidee L1 bis L5, Bänder unter 50, 50 bis unter 75, ab 75 Prozent | am Rahmenplan benannt, bewusst keine amtlichen Stufen |
| PL-3 | 24.11.2026 | Simulation: 12 fiktive Schulen, 600 Kinder, Beginn Klasse 5 und 6, ein Instrument | Vergleich nur mit gleichem Instrument sinnvoll |
| PL-4 | 24.11.2026 | Gruppenmerkmale nur Schulart und Raumtyp | Datenminimierung; Förderbedarf wäre begründungspflichtige Ausnahme |
| PL-5 | 24.11.2026 | Grundsatz „nicht vergleichbar“, Ausnahmen nur mit Freigabe | fachlich begründete Vergleichbarkeit |
| PL-6 | 24.11.2026 | SQLite, pandas, Matplotlib, statischer HTML-Bericht; kein Docker, kein Streamlit | Reproduzierbarkeit vor Komplexität |
| PL-7 | 24.11.2026 | Abruf der vier Dateien, Installation in eigener Umgebung | |
| PL-8 | 24.11.2026 | Noreply-Adresse in Commits | Schutz der privaten E-Mail |
| PL-9 | 24.11.2026 | Gate 2, real: F1 Ämterabgleich, F2/F5 IQB-Trend, F3/F4 M-V gegen Deutschland freigegeben | einzeln freigegeben, kein Ranking |
| PL-10 | 24.11.2026 | Gate 2, simuliert: F6 Klasse 5 zu 6, F7 Gruppenvergleiche freigegeben | beschreibend, Mindestgröße 10 |
| PL-11 | 24.11.2026 | Öffentliches Repository ohne persönliche Arbeitsunterlagen | |
| PL-12 | 24.11.2026 | Testlänge bleibt bei 20 Aufgaben je Leitidee | Vergleich der Testlängen (KI-9) |
| PL-13 | 24.11.2026 | Punkte und Gewichte der Entscheidungsmatrix bestätigt | Vorschlag KI, siehe Machbarkeitsanalyse |
| PL-14 | 24.11.2026 | Keine Meldung der Dateifehler an das IQB | Befunde bleiben im Datenqualitätsbericht dokumentiert |
| PL-15 | 24.11.2026 | MIT-Lizenz für den Programmcode | Inhalte der Herausgeber ausgenommen |
| PL-16 | 24.11.2026 | Grenze ergänzt: Simulation ohne Förder-, Waldorfschulen und Gymnasien; keine neuen Daten | fehlende Schularten offen benennen |
| PL-17 | 24.11.2026 | Bandname „Unterstützung prüfen“ bleibt | fordert zum Hinsehen auf, ohne zu etikettieren |
| PL-18 | 24.11.2026 | Gymnasium in Klasse 5/6 bleibt offene Frage | ohne Beleg keine Erklärung |
| PL-19 | 24.11.2026 | Einzelne Kinder: kein Band je Leitidee, nur Gesamtergebnis, nie alleinige Grundlage für Förderung | Testlängenvergleich (KI-9) |
| PL-20 | 24.11.2026 | Grenzen ergänzt: Sprache und Lesen, Nachteilsausgleich | fachliche Aussagekraft |

Die Empfehlungen stammten jeweils vom KI-Assistenten, die Entscheidung von der Projektleitung.

## Technische Umsetzung und Festlegungen (KI)

| Nr. | Festlegung | Begründung |
|---|---|---|
| KI-1 | Import über Spaltenverträge mit Abbruch bei Abweichung | verhindert still verschobene Spalten |
| KI-2 | Schreibfehler nur über feste Aliasliste | kein unscharfes Raten |
| KI-3 | Negative Standardfehler verwerfen, Wert behalten | Vorzeichen nicht raten |
| KI-4 | Veränderungen des IQB übernehmen statt berechnen | veröffentlichte Standardfehler sind nicht aus Einzelwerten ableitbar |
| KI-5 | Bootstrap über Schulen statt über Klassen (**Abweichung vom Plan**, zur Kenntnis PL) | Gruppenmerkmale liegen auf Schulebene |
| KI-6 | pypdf zusätzlich zu openpyxl (**Abweichung vom Plan**, zur Kenntnis PL) | Q4 liegt nur als PDF vor |
| KI-7 | Startwert nicht angepasst, obwohl L5 den gesetzten Wert verfehlt | Ergebnisse nicht zurechtrücken |
| KI-8 | Analyse der Einstufungssicherheit ergänzt | Bänder ohne Unsicherheit wären irreführend |
| KI-9 | Testlänge 10 bis 100 Aufgaben verglichen (Auftrag PL: 40 Aufgaben testen), Hauptlauf unverändert bei 20 | Entscheidung vorbereiten |
| KI-10 | Darstellung korrigiert: „Bereich berührt Bandgrenze“ (über 80 %) ist nicht „falsch eingestuft“ (rund 26 %) | erste Fassung war missverständlich |
| KI-11 | Spalte `band` aus `fact_simulation` entfernt, Sicht `v_sim_kind_gesamt` ergänzt | Umsetzung PL-19 im Datenmodell |

## Offen für die Projektleitung

Fachliche Abnahme der Ergebnisse.
