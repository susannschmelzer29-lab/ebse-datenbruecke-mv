# Datenquellenkatalog

Alle Abrufe am 24.11.2026. Prüfsummen: [`data/raw/manifest.json`](../data/raw/manifest.json). Rohdateien werden nicht
weitergegeben, sondern mit `python -m src.ingestion.fetch` direkt beim Herausgeber geladen.

## Verwendete reale Quellen (aggregiert)

### Q1 Statistischer Bericht Allgemeinbildende Schulen 2025/26
| | |
|---|---|
| Herausgeber | Statistisches Bundesamt (Destatis), Artikelnummer 2110100267005 |
| Inhalt | Schüler, Klassen, Wiederholer nach Klassenstufe und Schulart |
| Bezugsjahr, Raum | Schuljahr 2025/26, Deutschland und Länder |
| Format | XLSX, 8,5 MB, 55 Blätter, davon 24 maschinenlesbare „csv-“-Blätter |
| Lizenz | „Vervielfältigung und Verbreitung, auch auszugsweise, mit Quellenangabe gestattet.“ (Blatt Impressum) |
| Abruf | [Direktlink](https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Bildung-Forschung-Kultur/Schulen/Publikationen/Downloads-Schulen/statistischer-bericht-allgemeinbildende-schulen-2110100267005.xlsx?__blob=publicationFile&v=3), ohne Anmeldung |
| Einschränkungen | keine Leistungsdaten; Tabellen verwenden verschiedene Grundgesamtheiten |
| Verwendung | Kontextdaten Klasse 5/6; Blätter csv-21111-02, -04, -07 |

### Q2 IQB-Bildungstrend 2024, Zusatzmaterial Tabellen
| | |
|---|---|
| Herausgeber | IQB; Stanat, Schipolowski, Gentrup, Sachse, Weirich, Henschel (Hrsg.) |
| Inhalt | Mathematik Klasse 9: Mittelwerte, Streuungen, Mindeststandards mit Standardfehlern |
| Bezugsjahr, Raum | 2012, 2018, 2024; Deutschland und Länder |
| Format | XLSX, 3,5 MB, 203 Blätter, Stand 25.06.2026 |
| Lizenz | **CC BY-NC-SA 4.0** (Titelblatt) |
| Abruf | [Direktlink](https://www.iqb.hu-berlin.de/media/documents/2026-06-26_IQB-Bildungtrend_2024_Zusatzmaterial_Tabellen.xlsx), ohne Anmeldung |
| Einschränkungen | Stichprobe, Landesebene, Klasse 9; nicht mit Klasse 5/6 vergleichbar |
| Verwendung | Tab. 4.1web bis 4.6web (alle Neuntklässler), Tab. 3.25web bis 3.30web (zielgleich Unterrichtete) |

### Q3 IQB-Bildungstrend 2021, Zusatzmaterial Tabellen
| | |
|---|---|
| Herausgeber | IQB; Stanat, Schipolowski, Schneider, Sachse, Weirich, Henschel (Hrsg.) |
| Inhalt | Mathematik Klasse 4: Globalskala und fünf Leitideen |
| Bezugsjahr, Raum | 2011, 2016, 2021; Deutschland und Länder, **M-V nicht ausgewiesen** |
| Format | XLSX, 0,4 MB, 40 Blätter, Stand 06.03.2023 |
| Lizenz | in Titelblatt und Downloadseite keine Angabe gefunden; vor Weiterverwendung klären |
| Abruf | [Direktlink](https://www.iqb.hu-berlin.de/media/documents/IQB_Bildungstrend2021_Zusatzmaterial_Tabellen.xlsx), ohne Anmeldung |
| Einschränkungen | nur in einem Fünftel der in M-V vorgesehenen Schulen fanden Testsitzungen statt |
| Verwendung | Qualitätsprüfung und Nachweis der Datenlücke; keine Werte im öffentlichen Repository |

### Q4 Statistischer Bericht B1131 2025 00
| | |
|---|---|
| Herausgeber | Statistisches Amt Mecklenburg-Vorpommern, 16.09.2026 |
| Inhalt | Schulen, Klassen, Schüler |
| Bezugsjahr, Raum | Schuljahr 2025/26, Mecklenburg-Vorpommern |
| Format | PDF, 1,5 MB, 44 Seiten |
| Lizenz | „Auszugsweise Vervielfältigung und Verbreitung mit Quellenangabe gestattet.“ |
| Abruf | [Direktlink](https://www.laiv-mv.de/static/LAIV/Statistik/Dateien/Publikationen/B%20I%20Allgemeinbildende%20Schulen/B%201131/B1131%202025%2000.pdf), ohne Anmeldung |
| Einschränkungen | PDF, deshalb nur ein enger Ausschnitt; deutsches Zahlenformat |
| Verwendung | Tabelle 1.9, Jahrgangsstufe 5 und 6, als Gegenprobe zu Q1 (vermutlich dieselbe Erhebung) |

## Simulierte Daten (SIM)

Eigene, vollständig künstliche Individualdaten: 12 fiktive Schulen, 600 fiktive Kinder, zwei Messzeitpunkte, Mathematik
Klasse 5 und 6. Dateien `data/simulated/SIM_*`. Parameter frei gesetzt, nicht aus realen Ergebnissen abgeleitet.

## Geprüft und nicht verwendet

| Quelle | Grund |
|---|---|
| Amtliches Schulverzeichnis M-V ([WFS](https://gdk.gdi-de.org/geonetwork/srv/api/records/d3f4b0c0-6583-41f7-a798-1d0231128504)) | enthält Namen von Schulleitungen; echte Schulen sollen nicht neben simulierten Leistungsdaten stehen |
| [IQB-BT 2021, Scientific Use File](https://fdz.iqb.hu-berlin.de/en/find-data/search/141/) | Individualdaten nur auf Antrag, nicht frei verfügbar |
| IQB-Bildungstrend 2016 | gefundener Link lieferte Fehler 404 |
| Destatis-Bericht 2024/25 | für den Demonstrator nicht nötig |

## Fachliche Referenz

[Rahmenplan Mathematik, schulartunabhängige Orientierungsstufe 5/6, Juli 2026](https://www.bildung-mv.de/export/sites/bildungsserver/.galleries/dokumente/unterricht/rahmenplaene/RP-Mathematik-Orientierungsstufe-2026.pdf)
(Bildungsministerium M-V, IQ M-V): Leitideen L1 bis L5. Ein Kompetenzstufenmodell mit Schwellenwerten wurde darin nicht gefunden.
