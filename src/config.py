"""Zentrale Einstellungen: Pfade, Quellen, Simulationsparameter."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
SIMULATED = ROOT / "data" / "simulated"
REPORTS = ROOT / "reports"
DASHBOARD = ROOT / "dashboard"
DB = PROCESSED / "ebse.sqlite"
SCHEMA = ROOT / "database" / "schema.sql"
QUERIES = ROOT / "database" / "queries.sql"

LAND = "Mecklenburg-Vorpommern"

_DESTATIS = ("https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Bildung-Forschung-Kultur/"
             "Schulen/Publikationen/Downloads-Schulen/")
_IQB = "https://www.iqb.hu-berlin.de/media/documents/"

QUELLEN = {
    "Q1": dict(datei="Q1_destatis_allgemeinbildende_schulen_2025_26.xlsx",
               url=_DESTATIS + "statistischer-bericht-allgemeinbildende-schulen-2110100267005.xlsx"
                               "?__blob=publicationFile&v=3",
               titel="Statistischer Bericht Allgemeinbildende Schulen 2025/26",
               herausgeber="Statistisches Bundesamt (Destatis)", bezugsjahr="2025/26",
               raum="Deutschland und Länder", datenart="Vollerhebung, aggregiert",
               lizenz="Vervielfältigung und Verbreitung, auch auszugsweise, mit Quellenangabe gestattet"),
    "Q2": dict(datei="Q2_iqb_bildungstrend_2024_tabellen.xlsx",
               url=_IQB + "2026-06-26_IQB-Bildungtrend_2024_Zusatzmaterial_Tabellen.xlsx",
               titel="IQB-Bildungstrend 2024, Zusatzmaterial Tabellen (Klasse 9)",
               herausgeber="IQB", bezugsjahr="2012/2018/2024",
               raum="Deutschland und Länder", datenart="Stichprobe, aggregiert",
               lizenz="CC BY-NC-SA 4.0"),
    "Q3": dict(datei="Q3_iqb_bildungstrend_2021_tabellen.xlsx",
               url=_IQB + "IQB_Bildungstrend2021_Zusatzmaterial_Tabellen.xlsx",
               titel="IQB-Bildungstrend 2021, Zusatzmaterial Tabellen (Klasse 4)",
               herausgeber="IQB", bezugsjahr="2011/2016/2021",
               raum="Deutschland und Länder, M-V nicht ausgewiesen", datenart="Stichprobe, aggregiert",
               lizenz="keine Angabe gefunden"),
    "Q4": dict(datei="Q4_statamt_mv_B1131_2025_00.pdf",
               url="https://www.laiv-mv.de/static/LAIV/Statistik/Dateien/Publikationen/"
                   "B%20I%20Allgemeinbildende%20Schulen/B%201131/B1131%202025%2000.pdf",
               titel="Statistischer Bericht B1131 2025 00, Allgemeinbildende Schulen Teil 1",
               herausgeber="Statistisches Amt Mecklenburg-Vorpommern", bezugsjahr="2025/26",
               raum="Mecklenburg-Vorpommern", datenart="Vollerhebung, aggregiert",
               lizenz="Auszugsweise Vervielfältigung und Verbreitung mit Quellenangabe gestattet"),
}

# --- Simulation (Entscheidungen 2 bis 4 der Projektleitung) ---
SEED = 20261124
N_SCHULEN = 12
KLASSEN_JE_SCHULE = 2
N_KINDER = 600
ITEMS_JE_LEITIDEE = 20
MIN_GRUPPE = 10
BOOTSTRAP = 2000

LEITIDEEN = {
    "L1": "Zahl und Operation",
    "L2": "Größen und Messen",
    "L3": "Strukturen und funktionaler Zusammenhang",
    "L4": "Raum und Form",
    "L5": "Daten und Zufall",
}
# Untergrenze in Prozent; bewusst keine amtlichen Kompetenzstufen
BAENDER = [(0, "Unterstützung prüfen"), (50, "im Aufbau"), (75, "sicher")]


def band(prozent: float) -> str:
    name = BAENDER[0][1]
    for grenze, bez in BAENDER:
        if prozent >= grenze:
            name = bez
    return name
