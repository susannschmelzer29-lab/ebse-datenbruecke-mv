"""Interaktives Dashboard als eigenständige HTML-Datei (ohne Server, ohne externe Bibliotheken).

Alle Zahlen stammen aus der Datenbank oder den Ergebnisdateien. Es werden keine Einzeldatensätze
fiktiver Kinder eingebettet, nur Gruppenwerte.
"""
import json

import pandas as pd

from src.config import DASHBOARD, QUELLEN, REPORTS
from src.reporting.report import tab_real
from src.transformation.compare import SIM_VERFAHREN, NichtVergleichbar, pruefe, vergleiche

VORLAGE = __file__.replace("dashboard.py", "dashboard_vorlage.html")
ALLE, ZIEL = "V_IQB24_KL9_ALLE", "V_IQB24_KL9_ZIELGLEICH"


def _k(v, n=0) -> str:
    return f"{v:.{n}f}".replace(".", ",")


def _tsd(v) -> str:
    return f"{v:,.0f}".replace(",", ".")


def klasse9(con, r) -> dict:
    t, werte = r["iqb"], {}
    for z in t.itertuples():
        werte.setdefault(z.kennzahl, {}).setdefault(z.kompetenz_id, {})[z.jahr] = dict(
            mv=z.mv, mv_se=z.mv_se, de=z.de, de_se=z.de_se, regel=z.regel, fund=z.fundstelle_mv)
    bereiche = t[["kompetenz_id", "bezeichnung"]].drop_duplicates().sort_values("kompetenz_id")
    sig, delta = {}, {}
    for kid, zp, s in con.execute("SELECT kompetenz_id, zeitpunkt_id, sig_de FROM fact_aggregat WHERE verfahren_id = ? "
                                  "AND kennzahl = 'mittelwert' AND land_id = 'MV'", (ALLE,)):
        sig.setdefault(kid, {})[zp] = s
    for kid, land, w, se, s in con.execute(
            "SELECT kompetenz_id, land_id, wert, se, sig_zeit FROM fact_aggregat WHERE verfahren_id = ? AND land_id IN ('MV','DE') "
            "AND kennzahl = 'differenz_mittelwert' AND zeitpunkt_id = '2024-2012'", (ALLE,)):
        delta.setdefault(kid, {}).update({"mv": w, "se": se, "sig": s} if land == "MV" else {"de": w})
    return dict(bereiche=[dict(id=a, name=b) for a, b in bereiche.itertuples(index=False)], werte=werte, sig=sig, delta=delta)


def datenqualitaet(con, abgleich, n_real) -> dict:
    schueler = {}
    for kl, g in abgleich[abgleich.art != "Insgesamt"].groupby("klassenstufe"):
        g = g.sort_values("V_DESTATIS_SCHUELER", ascending=False)
        schueler[str(kl)] = [dict(art=z.art, wert=int(z.V_DESTATIS_SCHUELER), nur04=z.art in ("Förderschule", "Waldorfschule"))
                             for z in g.itertuples()]
    befunde = tab_real(con).fillna("").astype(str).values.tolist()
    fehler = con.execute("SELECT COUNT(*) FROM dq_befund WHERE quelle_id <> 'SIM' AND regel_id = 'DQ03'").fetchone()[0]
    luecken = con.execute("SELECT COUNT(DISTINCT kompetenz_id) FROM fact_aggregat WHERE status = 'nicht_ausgewiesen'").fetchone()[0]
    return dict(schueler=schueler, befunde=befunde, quellen=[[q, f"{q}: {d['titel']}"] for q, d in QUELLEN.items()],
                kacheln=[["Reale Werte mit Fundstelle", _tsd(sum(n_real.values()))],
                         ["Destatis und Stat. Amt gleich", f"{int(abgleich.stimmt.sum())} von {len(abgleich)}"],
                         ["Unmögliche Standardfehler", str(fehler)],
                         ["Skalen ohne M-V-Wert (Kl. 4, 2021)", f"{luecken} von 6"]])


def simulation(r) -> dict:
    p, v = r["profil"], r["veraenderung"].set_index("leitidee")
    profil = []
    for l, g in p.groupby("leitidee"):
        g = g.set_index("zeitpunkt")
        profil.append(dict(id=l, name=g.bezeichnung.iloc[0], diff=v["diff"][l],
                           **{t: [g.mittel[t], g.ki_u[t], g.ki_o[t]] for t in ("T1", "T2")}))
    a = pd.read_csv(REPORTS / "SIM_testlaenge_je_leitidee.csv").set_index("aufgaben")
    b = pd.read_csv(REPORTS / "SIM_testlaenge_gesamt.csv").set_index("aufgaben_je_leitidee")
    return dict(profil=profil, laenge=[dict(n=int(n), leit=a.falsch_prozent[n], ges=b.falsch_prozent[n]) for n in a.index])


def vergleichsfragen(con) -> list[dict]:
    """Urteile der echten Vergleichssperre, nicht nachgebaut."""
    def fakt(verf, land, kid, zp):
        return con.execute("SELECT fakt_id FROM fact_aggregat WHERE verfahren_id = ? AND land_id = ? AND kompetenz_id = ? "
                           "AND zeitpunkt_id = ? AND kennzahl = 'mittelwert'", (verf, land, kid, zp)).fetchone()[0]

    def werte(a, b):
        return lambda: vergleiche(con, fakt(*a), fakt(*b))["regel"]

    def regel(*x):
        return lambda: pruefe(con, *x)

    fragen = [
        ("M-V mit Deutschland, Klasse 9, 2024", werte((ALLE, "MV", "SEK1-0", "2024"), (ALLE, "DE", "SEK1-0", "2024"))),
        ("M-V 2012 mit M-V 2024, Klasse 9", werte((ALLE, "MV", "SEK1-0", "2012"), (ALLE, "MV", "SEK1-0", "2024"))),
        ("Klasse 4 (2021) mit Klasse 9 (2024)", regel("V_IQB21_KL4", ALLE, "mittelwert", "quelle")),
        ("M-V mit Deutschland, Klasse 4, 2021", werte(("V_IQB21_KL4", "MV", "PRIM-0", "2021"), ("V_IQB21_KL4", "DE", "PRIM-0", "2021"))),
        ("„Messen“ mit „Zahl“, Klasse 9, M-V", werte((ALLE, "MV", "SEK1-2", "2024"), (ALLE, "MV", "SEK1-1", "2024"))),
        ("Mittelwert mit Mindeststandard-Anteil, Klasse 9", regel(ALLE, ZIEL, "mittelwert", "quelle")),
        ("Schülerzahl: Destatis mit Statistischem Amt M-V", regel("V_DESTATIS_SCHUELER", "V_STATAMT_MV", "schueler_anzahl", "quelle")),
        ("Schülerzahl: Destatis Tabelle 04 mit Tabelle 07", regel("V_DESTATIS_SCHUELER", "V_DESTATIS_WIEDERHOLER", "schueler_anzahl", "quelle")),
        ("Fiktive Kinder: Beginn Klasse 5 mit Beginn Klasse 6", regel(SIM_VERFAHREN, SIM_VERFAHREN, "loesungsanteil", "zeit")),
        ("Fiktive Kinder mit IQB Klasse 9", regel(SIM_VERFAHREN, ALLE, "loesungsanteil", "quelle")),
    ]
    out = []
    for frage, f in fragen:
        try:
            rid = f()
            grund = con.execute("SELECT begruendung FROM vergleichsregel WHERE regel_id = ?", (rid,)).fetchone()[0]
            out.append(dict(frage=frage, erlaubt=True, text=f"Regel {rid}: {grund}"))
        except NichtVergleichbar as e:
            out.append(dict(frage=frage, erlaubt=False, text=str(e)))
    return out


def aussagen(r, abgleich) -> list[list]:
    b = r["iqb_bereiche"].set_index("bezeichnung")
    m = b.loc["Messen"]
    i = r["iqb"].query("kompetenz_id == 'SEK1-0' and jahr == 2024").set_index("kennzahl")
    s = abgleich[abgleich.klassenstufe == 5].set_index("art").V_DESTATIS_SCHUELER
    sim = {x["n"]: x for x in simulation(r)["laenge"]}[20]
    g = r["gruppen"].set_index("merkmal").loc["schulart"]
    return [
        [[f"Klasse 9, 2024: M-V {_k(i.mv['mittelwert'])}, Deutschland {_k(i.de['mittelwert'])} auf der Gesamtskala.", "Laut IQB kein signifikanter Unterschied."],
         [f"Nur „Messen“ liegt 2024 signifikant darunter ({_k(m.mv_2024)} zu {_k(m.de_2024)}).", "Ebenso 2012 und 2018."],
         ["Alle fünf Bereiche sind in M-V seit 2012 signifikant gesunken.", "Angabe des IQB."],
         [f"{_k(i.mv['ms_msa_verfehlt'], 1)} % der zielgleich Unterrichteten verfehlen den Mindeststandard MSA.", f"Deutschland {_k(i.de['ms_msa_verfehlt'], 1)} %."],
         ["Für Klasse 4 sind 2021 keine Ergebnisse für M-V ausgewiesen.", "Nur in einem Fünftel der vorgesehenen Schulen wurde getestet."],
         [f"Klasse 5: {_tsd(s['Insgesamt'])} oder {_tsd(s['Insgesamt'] - s['Förderschule'] - s['Waldorfschule'])} Kinder, je nach Tabelle.", "Die Differenz entspricht Förder- und Waldorfschulen."]],
        [["Quellen lassen sich nachvollziehbar und wiederholbar zusammenführen.", "Gezeigt an vier Dateien."],
         [f"20 Aufgaben je Leitidee: rund {_k(sim['leit'])} % falsche Bänder, beim Gesamtergebnis {_k(sim['ges'])} %.", "Simuliert."],
         [f"Schulartunterschied bei {g.schulen_a:.0f} gegen {g.schulen_b:.0f} Schulen nicht gesichert.", "Simuliert, obwohl ein Unterschied eingebaut war."],
         ["Zwei Ämter melden gleiche Zahlen.", "Zeigt konsistente Weitergabe. Vermutlich dieselbe Erhebung, also keine unabhängige Bestätigung."],
         ["Einstieg über Dateien, langfristig modulare Plattform.", "Begründete Einschätzung, keine Messung."]],
        [["„Kinder in Klasse 5/6 sind schwach im Messen.“", "Keine öffentlichen Daten gefunden."],
         ["„Corona oder der Unterricht ist schuld.“", "Ursachen wurden nicht untersucht."],
         ["„Von Klasse 4 bis 9 wird es schlechter.“", "Andere Kinder, andere Tests, andere Skalen."],
         ["„Gesamtschulen sind besser.“", "Simuliert und nicht gesichert."],
         ["„In M-V gibt es keine Daten zu Klasse 5.“", "Nur öffentlich nicht gefunden. Intern möglich, etwa aus LEO.MV."],
         ["„Das System findet alle Fehler.“", "Nur solche, für die es Regeln gibt."]]]


def daten(con, r, abgleich, n_real) -> dict:
    return dict(k9=klasse9(con, r), dq=datenqualitaet(con, abgleich, n_real), sim=simulation(r),
                vergleiche=vergleichsfragen(con), aussagen=aussagen(r, abgleich))


def schreibe(con, r, abgleich, n_real) -> None:
    with open(VORLAGE, encoding="utf-8") as f:
        vorlage = f.read()
    # "<" wird maskiert, damit Text aus den Quellen den JSON-Block nicht beenden kann
    js = json.dumps(daten(con, r, abgleich, n_real), ensure_ascii=False, default=float).replace("<", "\\u003c")
    (DASHBOARD / "dashboard.html").write_text(vorlage.replace("__DATEN__", js), encoding="utf-8", newline="\n")
