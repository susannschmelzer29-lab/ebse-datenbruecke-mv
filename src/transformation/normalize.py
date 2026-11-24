"""Rohwerte deuten: Zahlenformate und Bezeichnungen. Jede Änderung ist eine explizite Regel."""
import re

LAENDER = {
    "DE": "Deutschland", "BW": "Baden-Württemberg", "BY": "Bayern", "BE": "Berlin", "BB": "Brandenburg",
    "HB": "Bremen", "HH": "Hamburg", "HE": "Hessen", "MV": "Mecklenburg-Vorpommern", "NI": "Niedersachsen",
    "NW": "Nordrhein-Westfalen", "RP": "Rheinland-Pfalz", "SL": "Saarland", "SN": "Sachsen",
    "ST": "Sachsen-Anhalt", "SH": "Schleswig-Holstein", "TH": "Thüringen"}
LAND_ID = {v: k for k, v in LAENDER.items()}

# In den Originaldateien belegte Schreibfehler. Kein unscharfes Raten: Unbekanntes bricht ab.
LAND_ALIAS = {"Mecklenburg-Vormpommern": "Mecklenburg-Vorpommern", "Niedersachen": "Niedersachsen"}

# Nur für Mecklenburg-Vorpommern: dort bilden diese Destatis-Gruppen die genannten Schularten ab.
# Abgesichert durch den zahlengenauen Abgleich Q1 gegen Q4 (Regel DQ10).
SCHULFORM_MV = {
    ("Q1", "Schularten mit zwei Bildungsgängen"): "Regionale Schule",
    ("Q1", "Schularten mit drei Bildungsgängen"): "Gesamtschule",
    ("Q1", "Gymnasien (G8)"): "Gymnasium",
    ("Q1", "Freie Waldorfschulen"): "Waldorfschule",
    ("Q1", "Förderschulen"): "Förderschule",
    ("Q1", "Insgesamt"): "Insgesamt",
    ("Q4", "Regionale Schule"): "Regionale Schule",
    ("Q4", "integrierte Gesamtschule"): "Gesamtschule",
    ("Q4", "Gymnasium"): "Gymnasium",
    ("Q4", "Waldorfschule"): "Waldorfschule",
    ("Q4", "Förderschule"): "Förderschule",
    ("Q4", "Insgesamt"): "Insgesamt"}


def land(roh: str) -> str:
    name = LAND_ALIAS.get(roh, roh)
    if name not in LAND_ID:
        raise ValueError(f"Unbekannte Landesbezeichnung: {roh!r}")
    return name


def zahl(roh, quelle_id: str):
    """Q4 ist ein deutsches PDF: '15.248' bedeutet 15248. Excel-Quellen nutzen den Dezimalpunkt."""
    if roh is None:
        return None
    if quelle_id == "Q4":
        if not re.fullmatch(r"\d{1,3}(\.\d{3})*", roh):
            raise ValueError(f"Q4: unerwartetes Zahlenformat {roh!r}")
        return float(roh.replace(".", ""))
    return round(float(roh), 6)
