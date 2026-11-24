"""Vergleichssperre: Zwei Werte dürfen nur verglichen werden, wenn eine Regel das freigibt."""
import sqlite3


class NichtVergleichbar(RuntimeError):
    pass


FELDER = ("verfahren_id, land_id, klassenstufe, schulform_id, kompetenz_id, zeitpunkt_id, "
          "kennzahl, wert, se, status")
SIM_VERFAHREN = "V_SIM_MATHE_OS"


def pruefe(con: sqlite3.Connection, verfahren_a: str, verfahren_b: str, kennzahl: str, dimension: str) -> str:
    """Liefert die Regel-ID oder wirft NichtVergleichbar mit verständlicher Begründung."""
    regeln = con.execute(
        "SELECT regel_id, status, begruendung FROM vergleichsregel "
        "WHERE kennzahl IN (?, '*') AND dimension = ? "
        "AND ((verfahren_a = ? AND verfahren_b = ?) OR (verfahren_a = ? AND verfahren_b = ?)) "
        "ORDER BY regel_id",
        (kennzahl, dimension, verfahren_a, verfahren_b, verfahren_b, verfahren_a)).fetchall()
    for status, text in (("gesperrt", "{0} gesperrt: {1}"),
                         ("vorgeschlagen", "{0} ist vorgeschlagen, aber fachlich noch nicht freigegeben.")):
        frei = [r for r in regeln if r[1] == "freigegeben"]
        if status == "vorgeschlagen" and frei:
            return frei[0][0]
        treffer = [r for r in regeln if r[1] == status]
        if treffer:
            raise NichtVergleichbar(text.format(treffer[0][0], treffer[0][2]))
    raise NichtVergleichbar(
        f"Keine Regel für {verfahren_a} und {verfahren_b} ({kennzahl}, {dimension}). "
        "Ohne begründete Freigabe gilt: nicht vergleichbar.")


def hole(con, fakt_id: int) -> dict:
    cur = con.execute(f"SELECT {FELDER} FROM fact_aggregat WHERE fakt_id = ?", (fakt_id,))
    zeile = cur.fetchone()
    if zeile is None:
        raise KeyError(fakt_id)
    return dict(zip([c[0] for c in cur.description], zeile))


def _harmonisiert(con, schulform_id):
    r = con.execute("SELECT harmonisiert_mv FROM dim_schulform WHERE schulform_id = ?",
                    (schulform_id,)).fetchone()
    return r[0] if r else None


def vergleiche(con, fakt_a: int, fakt_b: int) -> dict:
    """Vergleicht zwei reale Aggregatwerte. Genau eine Dimension darf sich unterscheiden."""
    a, b = hole(con, fakt_a), hole(con, fakt_b)
    if a["kennzahl"] != b["kennzahl"]:
        raise NichtVergleichbar("Unterschiedliche Kennzahlen.")
    if a["klassenstufe"] != b["klassenstufe"]:
        raise NichtVergleichbar("Unterschiedliche Klassenstufen: andere Kohorten, kein Lernverlauf.")
    if a["kompetenz_id"] != b["kompetenz_id"]:
        raise NichtVergleichbar("Unterschiedliche Kompetenzbereiche oder Rahmen.")
    if "nicht_ausgewiesen" in (a["status"], b["status"]):
        raise NichtVergleichbar("Mindestens ein Wert ist nicht ausgewiesen. Fehlend ist nicht null.")
    unterschied = [d for d, u in (("quelle", a["verfahren_id"] != b["verfahren_id"]),
                                  ("land", a["land_id"] != b["land_id"]),
                                  ("zeit", a["zeitpunkt_id"] != b["zeitpunkt_id"])) if u]
    if len(unterschied) != 1:
        raise NichtVergleichbar("Es muss sich genau eine Dimension unterscheiden, "
                                f"gefunden: {', '.join(unterschied) or 'keine'}.")
    # Zuerst die Regel, damit die fachliche Begründung einer Sperre sichtbar wird
    regel = pruefe(con, a["verfahren_id"], b["verfahren_id"], a["kennzahl"], unterschied[0])
    if unterschied[0] == "quelle":
        h = _harmonisiert(con, a["schulform_id"])
        if a["land_id"] != "MV" or h is None or h != _harmonisiert(con, b["schulform_id"]):
            raise NichtVergleichbar("Schulformen sind zwischen den Quellen nicht zugeordnet.")
    elif a["schulform_id"] != b["schulform_id"]:
        raise NichtVergleichbar("Unterschiedliche Schulformen.")
    return {"regel": regel, "a": a["wert"], "b": b["wert"], "differenz": b["wert"] - a["wert"]}
