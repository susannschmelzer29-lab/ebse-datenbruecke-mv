# EBSE-Datenbrücke M-V

Demonstrator für modulares Datenmanagement und Kompetenzmonitoring in Mathematik, Klassenstufe 5 und 6.

> **Eigenständiger Prototyp.** Kein Produkt und keine Veröffentlichung des Bildungsministeriums Mecklenburg-Vorpommern.
> Individuelle Kompetenzdaten sind **vollständig simuliert** und sagen nichts über reale Kinder oder Schulen aus.

## Fragestellung

Wie können unterschiedliche Bildungsdatenquellen strukturiert, qualitätsgesichert und integriert werden, damit
Kompetenzentwicklungen transparent und reproduzierbar auswertbar sind?

## Ergebnisse in Kürze

| Frage | Ergebnis |
|---|---|
| Stimmen amtliche Quellen überein? | 12 von 12 Schülerzahlen für Klasse 5/6 in M-V sind bei Destatis und Statistischem Amt M-V gleich |
| Sind veröffentlichte Tabellen fehlerfrei? | Nein. Gefunden: abweichende Landesnamen, acht negative Standardfehler, eine fehlende Teilzeile |
| Bedeutet gleicher Name gleicher Inhalt? | Nein. „Schülerzahl Klasse 5“: 15.248 oder 14.539, je nach Tabelle |
| Gibt es öffentliche Kompetenzdaten für Klasse 5/6? | Keine gefunden. Für Klasse 4 (2021) weist das IQB für M-V keine Ergebnisse aus |
| Dürfen alle Werte verglichen werden? | Nein. Ohne begründete Freigabe weist das System jeden Vergleich ab |
| Taugt ein Kurztest zur Einzeleinstufung? | In der Simulation nur begrenzt: Mit 20 Aufgaben je Leitidee wäre rund jedes vierte Band falsch, mit 40 Aufgaben knapp jedes fünfte |

## Ansehen

- **Bericht:** `dashboard/index.html` herunterladen und im Browser öffnen, kein Server nötig
- [Datenqualitätsbericht](reports/datenqualitaetsbericht.md) · [Bildungsanalyse](reports/bildungsanalyse.md)
- [Datenquellen](docs/data_sources.md) · [Datenmodell](docs/data_model.md) · [Datenwörterbuch](docs/data_dictionary.md)
- [Machbarkeitsanalyse](docs/feasibility_analysis.md) · [Grenzen](docs/limitations.md) · [Entscheidungen](DECISION_LOG.md)

## Ausführen

Voraussetzung: Python 3.14, Git, Internet beim ersten Lauf (rund 14 MB).

```powershell
python -m venv .venv
```
```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```
```powershell
.venv\Scripts\python.exe -m src.run_all
```
```powershell
.venv\Scripts\python.exe -m pytest
```

Zusatzexperimente: `python -m src.analytics.testlaenge` und `python -m src.analytics.coverage`.

Der Gesamtlauf dauert etwa 15 Sekunden und erzeugt Datenbank, Grafiken und Berichte neu.

## Aufbau

```
Rohdaten (unverändert, SHA-256)           Simulation (fester Startwert)
        |                                          |
   src/ingestion  Spaltenverträge            data/simulated
        |                                          |
        +-------->  src/quality  12 Regeln  <------+
                        |  markieren, nie stillschweigend löschen
                src/transformation  SQLite, Herkunft je Wert
                    fact_aggregat | fact_simulation   (getrennt)
                        |
                Vergleichssperre (Positivliste)
                        |
                src/analytics, src/reporting -> reports, dashboard
```

| Ordner | Inhalt |
|---|---|
| `data/raw` | Originaldateien (nicht im Repository), Manifest mit Prüfsummen |
| `data/simulated` | simulierte Daten, Fehlerprotokoll, Parameter |
| `database` | Schema und Beispielabfragen |
| `src` | Programmcode |
| `tests` | 36 automatisierte Tests |
| `docs`, `reports`, `dashboard` | Dokumentation und Ergebnisse |

## Arbeitsweise

Human-in-the-Loop: Die Projektleitung hat Fragestellung, Datenquellen, Kompetenzbänder, Simulationsdesign, Gruppenmerkmale und
jede Vergleichsfreigabe entschieden. Recherche, Programmierung, Tests und Dokumentation wurden mit einem KI-Assistenten
(Claude Code) umgesetzt und im [Entscheidungslog](DECISION_LOG.md) getrennt ausgewiesen.

## Quellen und Lizenzhinweise

- Statistisches Bundesamt (Destatis), Statistischer Bericht Allgemeinbildende Schulen 2025/26. Eigene Auswahl und Darstellung.
- Statistisches Amt Mecklenburg-Vorpommern, Statistischer Bericht B1131 2025 00. Eigene Auswahl und Darstellung.
- IQB-Bildungstrend 2024, Zusatzmaterial Tabellen, Stanat et al. (Hrsg.), Stand 25.06.2026,
  [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). Verändert: Auswahl, Umrechnung, Grafik. Die daraus
  abgeleiteten Tabellen und Grafiken stehen unter derselben Lizenz.
- IQB-Bildungstrend 2021: keine Ergebniswerte im Repository, nur Befunde zur Dateiqualität.
- Für den Programmcode wurde noch keine Lizenz vergeben.
