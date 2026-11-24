"""Reale Quellen über Spaltenverträge einlesen.

Es werden nur ausdrücklich vereinbarte Zellen gelesen. Stimmt ein Tabellenkopf nicht mit dem
Vertrag überein, bricht der Import ab, statt falsche Spalten zu übernehmen. Werte werden hier
nicht korrigiert: `*_roh` enthält den Originaltext, die Deutung erfolgt in src/transformation.
"""
import re
import warnings

import openpyxl
import pandas as pd
from openpyxl.utils import get_column_letter
from pypdf import PdfReader

from src.config import QUELLEN, RAW

SPALTEN = ["quelle_id", "verfahren_id", "blatt", "zelle", "land_roh", "klassenstufe", "schulart_roh",
           "kompetenz_roh", "zeitpunkt", "kennzahl", "wert_roh", "se_roh", "se_zelle"]


class VertragFehler(RuntimeError):
    pass


def _wb(qid):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return openpyxl.load_workbook(RAW / QUELLEN[qid]["datei"], read_only=True, data_only=True)


def _text(v):
    return None if v is None else str(v)


def _erwarte(ist, soll, ort):
    if ist != soll:
        raise VertragFehler(f"{ort}: erwartet {soll!r}, gefunden {ist!r}")


def parse_q1() -> list[dict]:
    wb, out = _wb("Q1"), []
    vertraege = {
        "csv-21111-04": ("V_DESTATIS_SCHUELER", "Klassenstufe",
                         {"schulische_Herkunft": "Insgesamt", "Geschlecht": "Insgesamt"},
                         {"Schueler_innen_Anzahl": "schueler_anzahl"}),
        "csv-21111-07": ("V_DESTATIS_WIEDERHOLER", "Klassenstufe", {"Geschlecht": "Insgesamt"},
                         {"Schueler_innen_Anzahl": "schueler_anzahl",
                          "Anzahl_Wiederholer_innen": "wiederholer_anzahl",
                          "Wiederholer_innen_in_Prozent_Anteil": "wiederholer_anteil"}),
        "csv-21111-02": ("V_DESTATIS_KLASSEN", "Klassentypen", {}, {"Klassen_Anzahl": "klassen_anzahl"}),
    }
    for blatt, (verf, kl_spalte, filt, werte) in vertraege.items():
        zeilen = wb[blatt].iter_rows(values_only=True)
        kopf = list(next(zeilen))
        for sp in [kl_spalte, "Bundesland", "Schulart", "Schuljahr", *filt, *werte]:
            if sp not in kopf:
                raise VertragFehler(f"Q1/{blatt}: Spalte {sp} fehlt")
        ix = {sp: kopf.index(sp) for sp in kopf if sp}
        for nr, z in enumerate(zeilen, start=2):
            m = re.fullmatch(r"Klassenstufe ([56])", str(z[ix[kl_spalte]]))
            if not m or any(z[ix[s]] != v for s, v in filt.items()):
                continue
            # Zeilen, die nach Bildungsbereich mehrfach vorkommen, nur aus dem Sekundarbereich I
            # oder Primarbereich übernehmen, nicht zusätzlich aus Summenzeilen.
            for sp, kennzahl in werte.items():
                out.append(dict(quelle_id="Q1", verfahren_id=verf, blatt=blatt,
                                zelle=f"{get_column_letter(ix[sp] + 1)}{nr}",
                                land_roh=z[ix["Bundesland"]], klassenstufe=int(m[1]),
                                schulart_roh=z[ix["Schulart"]], kompetenz_roh=None,
                                zeitpunkt=z[ix["Schuljahr"]], kennzahl=kennzahl,
                                wert_roh=_text(z[ix[sp]]), se_roh=None, se_zelle=None))
    return out


def _trend_mittelwerte(ws, qid, verf, klasse, kompetenz, jahre, diffs):
    """Tabellen 'Mittelwerte und Streuungen im Trend': feste 7-Spalten-Blöcke je Jahr.

    Differenzen werden samt Standardfehler aus der Quelle übernommen und nicht selbst berechnet,
    weil die veröffentlichten Fehler auch die Verknüpfung der Messzeitpunkte berücksichtigen.
    """
    out, rows = [], list(ws.iter_rows(values_only=True))
    for k, jahr in enumerate(jahre):
        _erwarte(rows[4][1 + 7 * k], jahr, f"{qid}/{ws.title} Zeile 5")
        for off, soll in ((0, "M"), (2, "SE"), (3, "SD"), (5, "SE")):
            _erwarte(rows[5][1 + 7 * k + off], soll, f"{qid}/{ws.title} Zeile 6")
    for k, d in enumerate(diffs):
        _erwarte(rows[4][22 + 7 * k], d, f"{qid}/{ws.title} Zeile 5")
        _erwarte(rows[5][22 + 7 * k], "∆M", f"{qid}/{ws.title} Zeile 6")
        _erwarte(rows[5][24 + 7 * k], "SE", f"{qid}/{ws.title} Zeile 6")

    def rec(nr, z, zp, kz, c, sc):
        out.append(dict(quelle_id=qid, verfahren_id=verf, blatt=ws.title,
                        zelle=f"{get_column_letter(c + 1)}{nr}", land_roh=z[0], klassenstufe=klasse,
                        schulart_roh=None, kompetenz_roh=kompetenz, zeitpunkt=zp, kennzahl=kz,
                        wert_roh=_text(z[c]), se_roh=_text(z[sc]),
                        se_zelle=f"{get_column_letter(sc + 1)}{nr}"))

    for nr, z in enumerate(rows[6:], start=7):
        if not z[0] or not isinstance(z[1], (int, float)):
            continue
        for k, jahr in enumerate(jahre):
            rec(nr, z, str(jahr), "mittelwert", 1 + 7 * k, 3 + 7 * k)
            rec(nr, z, str(jahr), "standardabweichung", 4 + 7 * k, 6 + 7 * k)
        for k, d in enumerate(diffs):
            zp = d.replace("Differenz ", "").replace("–", "-")
            rec(nr, z, zp, "differenz_mittelwert", 22 + 7 * k, 24 + 7 * k)
    return out


def _standards(ws, qid, verf, klasse, kompetenz, jahre, labels):
    """Tabellen zu Mindest- und Regelstandard: Landname steht nur in der ersten Zeile des Blocks."""
    out, rows, land = [], list(ws.iter_rows(values_only=True)), None
    for k, jahr in enumerate(jahre):
        _erwarte(rows[4][2 + 3 * k], jahr, f"{qid}/{ws.title} Zeile 5")
        _erwarte(rows[5][2 + 3 * k], "%", f"{qid}/{ws.title} Zeile 6")
        _erwarte(rows[5][3 + 3 * k], "SE", f"{qid}/{ws.title} Zeile 6")
    for nr, z in enumerate(rows[6:], start=7):
        if z[0] and z[1]:
            land = z[0]
        if z[1] not in labels:
            continue
        for k, jahr in enumerate(jahre):
            c = 2 + 3 * k
            out.append(dict(quelle_id=qid, verfahren_id=verf, blatt=ws.title,
                            zelle=f"{get_column_letter(c + 1)}{nr}", land_roh=land, klassenstufe=klasse,
                            schulart_roh=None, kompetenz_roh=kompetenz, zeitpunkt=str(jahr),
                            kennzahl=labels[z[1]], wert_roh=_text(z[c]), se_roh=_text(z[c + 1]),
                            se_zelle=f"{get_column_letter(c + 2)}{nr}"))
    return out


def parse_q2() -> list[dict]:
    wb, out, jahre = _wb("Q2"), [], [2012, 2018, 2024]
    komp = ["Globalskala", "Zahl", "Messen", "Raum und Form", "Funktionaler Zusammenhang", "Daten und Zufall"]
    diffs = ["Differenz 2018–2012", "Differenz 2024–2018", "Differenz 2024–2012"]
    for i, k in enumerate(komp):
        out += _trend_mittelwerte(wb[f"Tab. 4.{1 + i}web"], "Q2", "V_IQB24_KL9_ALLE", 9, k, jahre, diffs)
        out += _standards(wb[f"Tab. 3.{25 + i}web"], "Q2", "V_IQB24_KL9_ZIELGLEICH", 9, k, jahre,
                          {"MS (ESA) verfehlt": "ms_esa_verfehlt", "MS (MSA) verfehlt": "ms_msa_verfehlt"})
    return out


def parse_q3() -> list[dict]:
    wb, out, jahre = _wb("Q3"), [], [2011, 2016, 2021]
    komp = ["Globalskala", "Zahlen und Operationen", "Raum und Form", "Muster und Strukturen",
            "Größen und Messen", "Daten, Häufigkeit und Wahrscheinlichkeit"]
    diffs = ["Differenz 2021-2016", "Differenz 2021-2011", "Differenz 2016-2011"]
    for i, k in enumerate(komp):
        out += _trend_mittelwerte(wb[f"Tab. 4.{4 + i}web"], "Q3", "V_IQB21_KL4", 4, k, jahre, diffs)
        out += _standards(wb[f"Tab. 3.{13 + i}web"], "Q3", "V_IQB21_KL4", 4, k, jahre,
                          {"MS verfehlt": "ms_verfehlt", "RS erreicht": "rs_erreicht"})
    return out


def q3_hinweis_mv() -> tuple[str, str]:
    """Fundstelle und Text des Hinweises, warum M-V 2021 nicht ausgewiesen ist."""
    for nr, z in enumerate(_wb("Q3")["Inhalt"].iter_rows(values_only=True), start=1):
        for v in z:
            if isinstance(v, str) and v.startswith("Hinweis: Für das Land Mecklenburg-Vorpommern"):
                return f"Inhalt, Zeile {nr}", v
    raise VertragFehler("Q3: Hinweis zu Mecklenburg-Vorpommern nicht gefunden")


def parse_q4() -> list[dict]:
    """Tabelle 1.9 (PDF-Seite 18): Schüler nach Schulart, nur Jahrgangsstufe 5 und 6."""
    text = PdfReader(RAW / QUELLEN["Q4"]["datei"]).pages[17].extract_text()
    if "Tabelle 1.9" not in text:
        raise VertragFehler("Q4: Tabelle 1.9 nicht auf PDF-Seite 18")
    kopf = ["Insgesamt", "Grundschule", "Regionale Schule", "Gymnasium", "integrierte Gesamtschule",
            "Waldorfschule", "Förderschule", "Abendgymnasium"]
    out = []
    for kl in (5, 6):
        m = re.search(rf"Jahrgangsstufe {kl} Schüler insgesamt ((?:[\d.]+|x)(?: (?:[\d.]+|x)){{7}})", text)
        if not m:
            raise VertragFehler(f"Q4: Zeile Jahrgangsstufe {kl} nicht lesbar")
        for sp, (art, w) in enumerate(zip(kopf, m[1].split()), start=1):
            if w != "x":  # x = Aussage nicht sinnvoll (Zeichenerklärung der Quelle)
                out.append(dict(quelle_id="Q4", verfahren_id="V_STATAMT_MV", blatt="Tabelle 1.9, S. 18",
                                zelle=f"Jg. {kl}, Wertspalte {sp}", land_roh="Mecklenburg-Vorpommern",
                                klassenstufe=kl, schulart_roh=art, kompetenz_roh=None, zeitpunkt="2025/26",
                                kennzahl="schueler_anzahl", wert_roh=w, se_roh=None, se_zelle=None))
    return out


def parse_all() -> pd.DataFrame:
    return pd.DataFrame(parse_q1() + parse_q2() + parse_q3() + parse_q4(), columns=SPALTEN)
