# Datenwörterbuch

## fact_aggregat (reale, aggregierte Werte)
| Feld | Bedeutung | Beispiel |
|---|---|---|
| fakt_id | technischer Schlüssel | 1 |
| quelle_id | Quelle Q1 bis Q4 | Q2 |
| verfahren_id | Erhebungsverfahren mit Grundgesamtheit und Skala | V_IQB24_KL9_ALLE |
| land_id | Landeskürzel, DE = Deutschland | MV |
| klassenstufe | 4, 5, 6 oder 9 | 9 |
| schulform_id | Schulform der Quelle, leer bei IQB | |
| kompetenz_id | Kompetenzbereich je Rahmen, leer bei Schulstatistik | SEK1-0 |
| zeitpunkt_id | Schuljahr, Erhebungsjahr oder Differenzzeitraum | 2024 |
| kennzahl | siehe unten | mittelwert |
| wert, se | gedeuteter Wert und Standardfehler | 471; 2,6 |
| status | gueltig, se_verworfen, nicht_ausgewiesen | gueltig |
| statusgrund | Begründung bei Abweichung | Negativer Standardfehler in der Quelle |
| wert_roh, se_roh, land_roh | unveränderter Originaltext | Mecklenburg-Vormpommern |
| blatt, zelle | Fundstelle in der Originaldatei | Tab. 4.1web, P14 |

**Kennzahlen**
| Kennzahl | Bedeutung | Einheit |
|---|---|---|
| schueler_anzahl, klassen_anzahl, wiederholer_anzahl | Anzahl | Anzahl |
| wiederholer_anteil | Anteil Wiederholender | Prozent |
| mittelwert, standardabweichung | Verteilung auf der IQB-Berichtsskala | Punkte |
| differenz_mittelwert | vom IQB berichtete Veränderung | Punkte |
| ms_verfehlt, rs_erreicht | Klasse 4: Mindeststandard verfehlt, Regelstandard erreicht | Prozent |
| ms_esa_verfehlt, ms_msa_verfehlt | Klasse 9: Mindeststandard für ESA bzw. MSA verfehlt | Prozent |

## fact_simulation (SIMULIERT)
| Feld | Bedeutung | Beispiel |
|---|---|---|
| kind_id | fiktives Kind | SIM-K0001 |
| zeitpunkt_id | T1 = Beginn Klasse 5, T2 = Beginn Klasse 6 | T1 |
| klassenstufe | 5 oder 6 | 5 |
| kompetenz_id | Leitidee L1 bis L5 | L1 |
| testdatum | fiktives Datum, JJJJ-MM-TT | 2025-09-15 |
| punkte, max_punkte | gelöste und gestellte Aufgaben | 13; 20 |
| roh_zeile | Zeile in SIM_ergebnisse_roh.csv | 2 |
| ist_simuliert | immer 1 | 1 |

`v_sim_kind_gesamt`: ein Band je Kind und Messzeitpunkt über alle fünf Leitideen, nur bei vollständigem Profil: Unterstützung prüfen (unter 50 %), im Aufbau (50 bis unter 75 %), sicher (ab 75 %). Je Leitidee wird für einzelne Kinder kein Band gespeichert.

`sim_schule`: schule_id, name („Fiktive Schule …“), schulart, raumtyp. `sim_kind`: kind_id, schule_id, klasse_id.
Nicht enthalten (Datenminimierung): Name, Geschlecht, Herkunft, Förderbedarf, Geburtsdatum.

## Dimensionen
| Tabelle | Inhalt |
|---|---|
| dim_datenquelle | Titel, Herausgeber, Lizenz, URL, SHA-256, Abrufzeit, Kennzeichen simuliert |
| dim_verfahren | Grundgesamtheit, Skala, Kennzeichen simuliert |
| dim_land | 16 Länder und Deutschland |
| dim_schulform | Bezeichnung je Quelle, Zuordnung nur für M-V |
| dim_kompetenz | Bezeichnung je Rahmen (IQB Klasse 4, IQB Klasse 9, Rahmenplan M-V) |
| dim_zeitpunkt | Art: Schuljahr, Erhebungsjahr, Differenz, Messzeitpunkt |

## Qualität und Vergleichbarkeit
| Tabelle | Inhalt |
|---|---|
| dq_regel | Regel DQ01 bis DQ12, Prüfart, Schweregrad |
| dq_befund | Regel, Quelle, Fundstelle, Feld, Rohwert, Meldung, Behandlung |
| vergleichsregel | zwei Verfahren, Kennzahl, Dimension, Status, Begründung, Entscheidung |
