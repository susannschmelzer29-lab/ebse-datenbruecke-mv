"""Automatisierte Datenqualitätsprüfung.

Grundsätze: Rohdaten bleiben unverändert. Jeder Verstoß wird mit Fundstelle, Rohwert und
Behandlung protokolliert. Nichts wird stillschweigend entfernt oder korrigiert.
"""
import re

import pandas as pd

from src.config import LEITIDEEN, QUELLEN
from src.transformation import normalize
from src.transformation.simulate import FENSTER, KLASSENSTUFE

REGELN = [
    ("DQ01", "Fehlende Werte", "Ein Ergebniswert ist leer.", "Fehler"),
    ("DQ02", "Duplikate", "Derselbe Schlüssel kommt mehrfach vor (exakt oder widersprüchlich).", "Fehler"),
    ("DQ03", "Ungültige Wertebereiche",
     "Punkte außerhalb 0 bis Maximum, Prozent außerhalb 0 bis 100, negativer Standardfehler.", "Fehler"),
    ("DQ04", "Inkonsistente Bezeichnungen", "Land oder Schulart weicht von der Referenzliste ab.", "Warnung"),
    ("DQ05", "Fehlerhafte Datumsangaben", "Datum ungültig oder außerhalb des Erhebungsfensters.", "Fehler"),
    ("DQ06", "Fehlende Identifikatoren", "Kind-, Schul- oder Fundstellenangabe fehlt.", "Fehler"),
    ("DQ07", "Unplausible Kombinationen",
     "Kombination widerspricht der Regel, kann aber eine belegte Ausnahme sein.", "Warnung"),
    ("DQ08", "Unterschiedliche Datenformate",
     "Zahl oder Datum in abweichender Schreibweise, eindeutig umwandelbar.", "Hinweis"),
    ("DQ09", "Fehlende Metadaten", "Lizenz, Maximalpunktzahl oder Kompetenzbereich fehlt.", "Warnung"),
    ("DQ10", "Quellenabgleich", "Zwei amtliche Quellen widersprechen sich.", "Fehler"),
    ("DQ11", "Vollständigkeit", "Eine erwartete Einheit ist nicht enthalten.", "Warnung"),
    ("DQ12", "Grundgesamtheit", "Gleich benannte Kennzahl meint verschiedene Grundgesamtheiten.", "Warnung"),
]

SCHULARTEN = {"regionale schule": "Regionale Schule", "reg. schule": "Regionale Schule",
              "regionalschule": "Regionale Schule", "gesamtschule": "Gesamtschule",
              "ges.schule": "Gesamtschule", "igs": "Gesamtschule"}
AUSSCHLUSS = "nicht ausgewertet, Rohzeile bleibt erhalten"


def _b(regel, quelle, ort, feld, roh, meldung, behandlung):
    return dict(regel_id=regel, quelle_id=quelle, fundstelle=ort, feld=feld,
                rohwert=None if roh is None else str(roh), meldung=meldung, behandlung=behandlung)


# ---------------------------------------------------------------- reale Daten
def pruefe_real(df: pd.DataFrame) -> list[dict]:
    out = []
    schluessel = ["verfahren_id", "land_roh", "klassenstufe", "schulart_roh", "kompetenz_roh", "zeitpunkt", "kennzahl"]
    ort = df.quelle_id + " / " + df.blatt + " / " + df.zelle

    for i in df.index[df.wert_roh.isna()]:
        out.append(_b("DQ01", df.quelle_id[i], ort[i], "wert", None, "Wert fehlt", AUSSCHLUSS))
    for i in df.index[df.duplicated(schluessel, keep=False)]:
        out.append(_b("DQ02", df.quelle_id[i], ort[i], "Schlüssel", df.wert_roh[i], "Schlüssel mehrfach", AUSSCHLUSS))
    for i in df.index[df.blatt.isna() | df.zelle.isna()]:
        out.append(_b("DQ06", df.quelle_id[i], "unbekannt", "fundstelle", None, "Fundstelle fehlt", AUSSCHLUSS))
    for i in df.index[~df.zeitpunkt.astype(str).str.fullmatch(r"20\d\d(/\d\d|-20\d\d)?")]:
        out.append(_b("DQ05", df.quelle_id[i], ort[i], "zeitpunkt", df.zeitpunkt[i], "Zeitangabe ungültig", AUSSCHLUSS))

    for i, z in df.iterrows():
        wert = normalize.zahl(z.wert_roh, z.quelle_id) if isinstance(z.wert_roh, str) else None
        se = normalize.zahl(z.se_roh, z.quelle_id) if isinstance(z.se_roh, str) else None
        if se is not None and se < 0:
            out.append(_b("DQ03", z.quelle_id, f"{z.quelle_id} / {z.blatt} / {z.se_zelle}", "se", z.se_roh,
                          "Negativer Standardfehler ist rechnerisch unmöglich",
                          "Standardfehler verworfen, Wert bleibt; Vorzeichen wird nicht geraten"))
        prozent = z.kennzahl.startswith(("ms_", "rs_")) or z.kennzahl == "wiederholer_anteil"
        anzahl = z.kennzahl.endswith("_anzahl")
        if wert is not None and ((prozent and not 0 <= wert <= 100) or (anzahl and wert < 0)):
            out.append(_b("DQ03", z.quelle_id, ort[i], "wert", z.wert_roh, "Wert außerhalb des Bereichs", AUSSCHLUSS))
        if z.land_roh in normalize.LAND_ALIAS:
            out.append(_b("DQ04", z.quelle_id, ort[i], "land", z.land_roh,
                          f"Schreibweise weicht ab, gemeint: {normalize.LAND_ALIAS[z.land_roh]}",
                          "über dokumentierte Aliasliste zugeordnet, Rohwert erhalten"))
        if z.klassenstufe in (5, 6) and z.land_roh == "Mecklenburg-Vorpommern" \
                and str(z.schulart_roh).startswith("Gymnas") and z.kennzahl == "schueler_anzahl":
            out.append(_b("DQ07", z.quelle_id, ort[i], "schulart + klassenstufe", z.wert_roh,
                          "Gymnasium umfasst laut Q4 die Jahrgänge 7 bis 12, hier Klasse "
                          f"{z.klassenstufe}", "Wert bleibt gültig, Ausnahme fachlich klären"))

    # Formate je Tabelle zusammengefasst, damit der Bericht lesbar bleibt
    artefakt = df[df.quelle_id.isin(["Q1", "Q2", "Q3"])].melt(
        id_vars=["quelle_id", "blatt"], value_vars=["wert_roh", "se_roh"], value_name="roh")
    artefakt = artefakt[artefakt.roh.astype(str).str.contains(r"\.\d{10,}")]
    for (q, bl), g in artefakt.groupby(["quelle_id", "blatt"]):
        out.append(_b("DQ08", q, f"{q} / {bl}", "wert, se", g.roh.iloc[0],
                      f"{len(g)} Werte mit Gleitkommaresten", "auf 6 Nachkommastellen gerundet, Rohwert erhalten"))
    tausender = df[(df.quelle_id == "Q4") & df.wert_roh.str.contains(".", regex=False, na=False)]
    for bl, g in tausender.groupby("blatt"):
        out.append(_b("DQ08", "Q4", f"Q4 / {bl}", "wert", g.wert_roh.iloc[0],
                      f"{len(g)} Werte mit deutschem Tausenderpunkt (15.248 bedeutet 15248)",
                      "nach Zahlenvertrag der Quelle umgewandelt"))

    for qid, q in QUELLEN.items():
        if q["lizenz"].startswith("keine Angabe"):
            out.append(_b("DQ09", qid, qid, "lizenz", q["lizenz"], "Keine Lizenzangabe gefunden",
                          "Rohdatei wird nicht weitergegeben, Klärung mit Herausgeber"))
    for qid, g in df[df.quelle_id.isin(["Q2", "Q3"])].groupby("quelle_id"):
        fehlt = set(normalize.LAND_ID) - {normalize.land(x) for x in g.land_roh.unique()}
        for l in sorted(fehlt):
            out.append(_b("DQ11", qid, qid, "land", None, f"{l} hat keine Ergebniszeilen",
                          "als 'nicht ausgewiesen' mit Grund geführt, kein Ersatzwert"))

    mv = df[(df.land_roh == "Mecklenburg-Vorpommern") & (df.kennzahl == "schueler_anzahl")].copy()
    mv["wert"] = [normalize.zahl(w, q) for w, q in zip(mv.wert_roh, mv.quelle_id)]
    mv["art"] = [normalize.SCHULFORM_MV.get((q, s)) for q, s in zip(mv.quelle_id, mv.schulart_roh)]
    # Teilsummen: fehlt in einer Tabelle die Zeile einer Schulart, fällt das sonst nicht auf
    for (verf, kl), g in mv[mv.verfahren_id.str.startswith("V_DESTATIS")].groupby(["verfahren_id", "klassenstufe"]):
        gesamt = g[g.art == "Insgesamt"].wert.sum()
        teile = g[g.art != "Insgesamt"].wert.sum()
        if gesamt != teile:
            out.append(_b("DQ11", "Q1", f"{g.blatt.iloc[0]}, Klasse {kl}", "Teilsumme", f"{gesamt:.0f} / {teile:.0f}",
                          f"Schularten ergeben {gesamt - teile:.0f} weniger als Insgesamt; vorhanden: "
                          + ", ".join(sorted(g[g.art != "Insgesamt"].art)),
                          "Summenzeile der Quelle verwendet, fehlende Zeile nicht ergänzt"))
    tab = mv.pivot_table(index=["klassenstufe", "art"], columns="verfahren_id", values="wert", aggfunc="first")
    for (kl, art), z in tab.iterrows():
        d, s = z.get("V_DESTATIS_SCHUELER"), z.get("V_STATAMT_MV")
        if pd.notna(d) and pd.notna(s) and d != s:
            out.append(_b("DQ10", "Q4", f"Klasse {kl}, {art}", "schueler_anzahl", f"{d} / {s}",
                          "Destatis und Statistisches Amt M-V weichen ab", "Klärung erforderlich"))
        w = z.get("V_DESTATIS_WIEDERHOLER")
        if art == "Insgesamt" and pd.notna(d) and pd.notna(w) and d != w:
            erklaert = sum(tab.loc[(kl, a), "V_DESTATIS_SCHUELER"] for a in ("Waldorfschule", "Förderschule"))
            text = ("Differenz entspricht genau Förder- und Waldorfschulen" if d - w == erklaert
                    else "Differenz nicht erklärt")
            out.append(_b("DQ12", "Q1", f"Klasse {kl}, Tabellen 04 und 07", "schueler_anzahl",
                          f"{d:.0f} / {w:.0f}", text, "Verfahren getrennt geführt, Vergleich gesperrt (S6)"))
    return out


def quellenabgleich(df: pd.DataFrame) -> pd.DataFrame:
    """Gegenüberstellung Destatis und Statistisches Amt M-V für den Bericht."""
    mv = df[(df.land_roh == "Mecklenburg-Vorpommern") & (df.kennzahl == "schueler_anzahl")
            & df.verfahren_id.isin(["V_DESTATIS_SCHUELER", "V_STATAMT_MV"])].copy()
    mv["wert"] = [int(normalize.zahl(w, q)) for w, q in zip(mv.wert_roh, mv.quelle_id)]
    mv["art"] = [normalize.SCHULFORM_MV.get((q, s)) for q, s in zip(mv.quelle_id, mv.schulart_roh)]
    t = mv.pivot(index=["klassenstufe", "art"], columns="verfahren_id", values="wert").reset_index()
    t.columns.name = None
    t["stimmt"] = t.V_DESTATIS_SCHUELER == t.V_STATAMT_MV
    return t


# ---------------------------------------------------------------- simulierte Daten
def _datum(text):
    for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
        try:
            return pd.to_datetime(text, format=fmt)
        except (ValueError, TypeError):
            continue
    return None


def _ganzzahl(text):
    m = re.fullmatch(r"(-?\d+)(,0+)?", text)
    return int(m[1]) if m else None


def pruefe_sim(roh: pd.DataFrame) -> tuple[list[dict], pd.DataFrame]:
    """Liefert Befunde und die auswertbaren, typisierten Zeilen. `roh` bleibt unverändert."""
    out, ok = [], []
    roh = roh.copy()
    roh["roh_zeile"] = range(2, len(roh) + 2)

    schluessel = ["kind_id", "messzeitpunkt", "leitidee"]
    inhalt = [c for c in roh.columns if c != "roh_zeile"]
    mit_id = roh[(roh.kind_id != "") & (roh.leitidee != "")]
    duplikat = {}
    for _, g in mit_id[mit_id.duplicated(schluessel, keep=False)].groupby(schluessel):
        if len(g[inhalt].drop_duplicates()) == 1:
            for z in g.roh_zeile.iloc[1:]:
                duplikat[z] = "exaktes Duplikat"
        else:
            for z in g.roh_zeile:
                duplikat[z] = "widersprüchliches Duplikat"

    for z in roh.itertuples():
        ort, fehler = f"SIM_ergebnisse_roh.csv / Zeile {z.roh_zeile}", False

        def melde(regel, feld, wert, text, behandlung=AUSSCHLUSS):
            out.append(_b(regel, "SIM", ort, feld, wert, text, behandlung) | {"roh_zeile": z.roh_zeile})

        if z.sim_kennzeichen != "SIMULIERT" or z.ist_simuliert != "1":
            raise ValueError(f"{ort}: Kennzeichnung als simuliert fehlt, Verarbeitung abgebrochen.")
        if z.kind_id == "" or z.schule_id == "":
            melde("DQ06", "kind_id", z.kind_id, "Identifikator fehlt")
            fehler = True
        if z.leitidee not in LEITIDEEN or z.max_punkte == "":
            melde("DQ09", "leitidee/max_punkte", f"{z.leitidee}|{z.max_punkte}", "Metadatum fehlt")
            fehler = True
        punkte = None
        if z.punkte == "":
            melde("DQ01", "punkte", z.punkte, "Punktwert fehlt")
            fehler = True
        else:
            punkte = _ganzzahl(z.punkte)
            if punkte is None or (z.max_punkte and not 0 <= punkte <= int(z.max_punkte)):
                melde("DQ03", "punkte", z.punkte, "Punkte außerhalb des gültigen Bereichs")
                fehler = True
            elif not re.fullmatch(r"-?\d+", z.punkte):
                melde("DQ08", "punkte", z.punkte, "Dezimalkomma", "eindeutig umgewandelt")
        datum = _datum(z.testdatum)
        von, bis = FENSTER[z.messzeitpunkt]
        if datum is None or not pd.Timestamp(von) <= datum <= pd.Timestamp(bis):
            melde("DQ05", "testdatum", z.testdatum, "Datum ungültig oder außerhalb des Erhebungsfensters")
            fehler = True
        elif not re.fullmatch(r"\d{4}-\d\d-\d\d", z.testdatum):
            melde("DQ08", "testdatum", z.testdatum, "deutsches Datumsformat", "eindeutig umgewandelt")
        art = SCHULARTEN.get(z.schulart.lower())
        if art != z.schulart:
            if art is None:
                melde("DQ04", "schulart", z.schulart, "unbekannte Schulart")
                fehler = True
            else:
                melde("DQ04", "schulart", z.schulart, f"gemeint: {art}", "über Aliasliste zugeordnet")
        if int(z.klassenstufe) != KLASSENSTUFE[z.messzeitpunkt]:
            melde("DQ07", "klassenstufe", z.klassenstufe, f"passt nicht zu {z.messzeitpunkt}")
            fehler = True
        if z.roh_zeile in duplikat:
            melde("DQ02", "Schlüssel", "|".join(getattr(z, s) for s in schluessel), duplikat[z.roh_zeile])
            fehler = True
        if not fehler:
            ok.append(dict(kind_id=z.kind_id, schule_id=z.schule_id, klasse_id=z.klasse_id, schulart=art,
                           raumtyp=z.raumtyp, zeitpunkt_id=z.messzeitpunkt, klassenstufe=int(z.klassenstufe),
                           kompetenz_id=z.leitidee, testdatum=datum.strftime("%Y-%m-%d"), punkte=punkte,
                           max_punkte=int(z.max_punkte), roh_zeile=z.roh_zeile))
    sauber = pd.DataFrame(ok)
    alle = set(roh.kind_id) - {""}
    for t in FENSTER:
        fehlend = len(alle - set(roh[roh.messzeitpunkt == t].kind_id))
        if fehlend:
            out.append(_b("DQ11", "SIM", f"Messzeitpunkt {t}", "kind_id", fehlend,
                          f"{fehlend} von {len(alle)} Kindern ohne Daten",
                          "bleibt fehlend, kein Ersatzwert; Veränderung nur für Kinder mit beiden Messungen")
                       | {"roh_zeile": None})
    return out, sauber


def erkennungsleistung(befunde: list[dict], protokoll: pd.DataFrame) -> pd.DataFrame:
    """Vergleicht Befunde mit den absichtlich eingebauten Fehlern."""
    gefunden = {(b["roh_zeile"], b["regel_id"]) for b in befunde if b.get("roh_zeile")}
    wahr = set(zip(protokoll.roh_zeile, protokoll.regel_id))
    zeilen = []
    for r in sorted({x[1] for x in wahr | gefunden}):
        w, g = {x for x in wahr if x[1] == r}, {x for x in gefunden if x[1] == r}
        zeilen.append(dict(regel_id=r, eingebaut=len(w), erkannt=len(w & g), uebersehen=len(w - g),
                           fehlalarm=len(g - w)))
    return pd.DataFrame(zeilen)
