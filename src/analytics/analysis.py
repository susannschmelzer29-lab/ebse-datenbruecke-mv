"""Exemplarische Auswertung der SIMULIERTEN Daten und freigegebener Vergleiche realer Aggregate.

Unsicherheit: Bootstrap über Schulen (nicht über Kinder), weil Kinder einer Schule einander
ähnlicher sind als zufällig gezogene Kinder. Bei 12 Schulen sind die Intervalle eher zu schmal.
"""
import sqlite3

import numpy as np
import pandas as pd

from src.config import BAENDER, BOOTSTRAP, LEITIDEEN, MIN_GRUPPE, SEED
from src.transformation.compare import SIM_VERFAHREN, NichtVergleichbar, pruefe, vergleiche
from src.transformation.simulate import PARAMETER

GRENZEN = [g for g, _ in BAENDER if g > 0]


def lade_sim(con) -> pd.DataFrame:
    df = pd.read_sql("SELECT * FROM v_simulation", con)
    if not (df.ist_simuliert == 1).all():
        raise RuntimeError("Nicht als simuliert gekennzeichnete Zeilen gefunden.")
    return df


def _bootstrap(df: pd.DataFrame, wert: str, rng) -> tuple[float, float, float]:
    """Mittelwert mit 95-%-Intervall, Ziehung ganzer Schulen mit Zurücklegen."""
    g = df.groupby("schule_id")[wert].agg(["sum", "count"])
    s, n = g["sum"].to_numpy(), g["count"].to_numpy()
    z = rng.integers(0, len(g), size=(BOOTSTRAP, len(g)))
    m = s[z].sum(1) / n[z].sum(1)
    u, o = np.percentile(m, [2.5, 97.5])
    return float(df[wert].mean()), float(u), float(o)


def _bootstrap_diff(a: pd.DataFrame, b: pd.DataFrame, wert: str, rng) -> tuple[float, float, float]:
    def zieh(df):
        g = df.groupby("schule_id")[wert].agg(["sum", "count"])
        z = rng.integers(0, len(g), size=(BOOTSTRAP, len(g)))
        return g["sum"].to_numpy()[z].sum(1) / g["count"].to_numpy()[z].sum(1)
    u, o = np.percentile(zieh(a) - zieh(b), [2.5, 97.5])
    return float(a[wert].mean() - b[wert].mean()), float(u), float(o)


def kompetenzprofil(df) -> pd.DataFrame:
    rng, out = np.random.default_rng(SEED), []
    for (t, l), g in df.groupby(["zeitpunkt_id", "kompetenz_id"]):
        m, u, o = _bootstrap(g, "prozent", rng)
        out.append(dict(zeitpunkt=t, leitidee=l, bezeichnung=LEITIDEEN[l], n=len(g), mittel=m, ki_u=u, ki_o=o,
                        sd=float(g.prozent.std(ddof=1))))
    return pd.DataFrame(out)


def baender(df) -> pd.DataFrame:
    t = df.groupby(["zeitpunkt_id", "kompetenz_id", "band"]).size().rename("n").reset_index()
    t["anteil"] = 100 * t.n / t.groupby(["zeitpunkt_id", "kompetenz_id"]).n.transform("sum")
    return t


def wahre_veraenderung(anzahl: int = 200_000) -> dict:
    """In der Simulation gesetzte Veränderung in Prozentpunkten (Erwartungswert, Monte Carlo)."""
    p, rng = PARAMETER, np.random.default_rng(SEED)
    konstant = np.sqrt(p["sd_schule"] ** 2 + p["sd_klasse"] ** 2 + p["sd_kind"] ** 2 + p["sd_kind_leitidee"] ** 2)
    # rund ein Drittel der fiktiven Schulen sind Gesamtschulen
    eta0 = rng.normal(0, konstant, anzahl) + p["effekt_gesamtschule"] * (rng.random(anzahl) < 1 / 3)
    sig = lambda x: 1 / (1 + np.exp(-x))
    out = {}
    for l in LEITIDEEN:
        a = sig(eta0 + p["basis_logit"][l] + rng.normal(0, p["sd_anlass"], anzahl))
        b = sig(eta0 + p["basis_logit"][l] + p["zuwachs_logit"][l] + rng.normal(0, p["sd_anlass"], anzahl))
        out[l] = float(100 * (b - a).mean())
    return out


def veraenderung(con, df) -> pd.DataFrame:
    pruefe(con, SIM_VERFAHREN, SIM_VERFAHREN, "loesungsanteil", "zeit")
    w = df.pivot_table(index=["kind_id", "schule_id", "kompetenz_id"], columns="zeitpunkt_id",
                       values="prozent").dropna().reset_index()
    w["diff"] = w.T2 - w.T1
    rng, wahr, out = np.random.default_rng(SEED + 1), wahre_veraenderung(), []
    for l, g in w.groupby("kompetenz_id"):
        m, u, o = _bootstrap(g, "diff", rng)
        out.append(dict(leitidee=l, bezeichnung=LEITIDEEN[l], n_gepaart=len(g), diff=m, ki_u=u, ki_o=o,
                        gesetzt=wahr[l], gesetzt_im_ki=u <= wahr[l] <= o))
    return pd.DataFrame(out)


def gruppen(con, df) -> pd.DataFrame:
    """Gruppenunterschiede zu T2, gemittelt über alle Leitideen je Kind. Beschreibend."""
    pruefe(con, SIM_VERFAHREN, SIM_VERFAHREN, "loesungsanteil", "gruppe")
    k = df[df.zeitpunkt_id == "T2"].groupby(["kind_id", "schule_id", "schulart", "raumtyp"]).agg(
        prozent=("prozent", "mean"), bereiche=("kompetenz_id", "nunique")).reset_index()
    k = k[k.bereiche == len(LEITIDEEN)]  # nur vollständige Profile, sonst verschiedene Aufgabenmischung
    rng, out = np.random.default_rng(SEED + 2), []
    for merkmal, a, b, gesetzt in (("schulart", "Gesamtschule", "Regionale Schule", PARAMETER["effekt_gesamtschule"]),
                                   ("raumtyp", "städtisch", "ländlich", PARAMETER["effekt_staedtisch"])):
        ga, gb = k[k[merkmal] == a], k[k[merkmal] == b]
        if min(len(ga), len(gb)) < MIN_GRUPPE:
            out.append(dict(merkmal=merkmal, gruppe_a=a, gruppe_b=b, unterdrueckt=True))
            continue
        d, u, o = _bootstrap_diff(ga, gb, "prozent", rng)
        out.append(dict(merkmal=merkmal, gruppe_a=a, gruppe_b=b, n_a=len(ga), n_b=len(gb),
                        schulen_a=ga.schule_id.nunique(), schulen_b=gb.schule_id.nunique(),
                        mittel_a=ga.prozent.mean(), mittel_b=gb.prozent.mean(), diff=d, ki_u=u, ki_o=o,
                        gesetzt_logit=gesetzt, unterdrueckt=False))
    return pd.DataFrame(out)


def wilson(k, n, z=1.96):
    p = k / n
    mitte = (p + z * z / (2 * n)) / (1 + z * z / n)
    halb = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return 100 * (mitte - halb), 100 * (mitte + halb)


def einstufungssicherheit(df) -> pd.DataFrame:
    """Anteil der Kinder, deren Messunsicherheit (Wilson, 95 %) über eine Bandgrenze reicht."""
    d = df.copy()
    d["u"], d["o"] = wilson(d.punkte.to_numpy(), d.max_punkte.to_numpy())
    d["unsicher"] = np.logical_or.reduce([(d.u < g) & (d.o >= g) for g in GRENZEN])
    t = d.groupby(["zeitpunkt_id", "kompetenz_id"]).agg(n=("unsicher", "size"), anteil=("unsicher", "mean")).reset_index()
    t["anteil"] *= 100
    return t


def iqb_mv(con) -> pd.DataFrame:
    """M-V und Deutschland, Klasse 9, je Kompetenzbereich und Jahr. Nur über die Vergleichssperre."""
    out = []
    for verf, kz in (("V_IQB24_KL9_ALLE", "mittelwert"), ("V_IQB24_KL9_ZIELGLEICH", "ms_msa_verfehlt")):
        f = pd.read_sql("SELECT fakt_id, land_id, kompetenz_id, k.bezeichnung, zeitpunkt_id, wert, se, blatt, zelle "
                        "FROM fact_aggregat JOIN dim_kompetenz k USING (kompetenz_id) "
                        "WHERE verfahren_id = ? AND kennzahl = ? AND land_id IN ('MV','DE')", con, params=(verf, kz))
        for (kid, bez, jahr), g in f.groupby(["kompetenz_id", "bezeichnung", "zeitpunkt_id"]):
            mv, de = g[g.land_id == "MV"].iloc[0], g[g.land_id == "DE"].iloc[0]
            v = vergleiche(con, int(de.fakt_id), int(mv.fakt_id))
            out.append(dict(kennzahl=kz, kompetenz_id=kid, bezeichnung=bez, jahr=int(jahr), mv=mv.wert, mv_se=mv.se,
                            de=de.wert, de_se=de.se, regel=v["regel"], fundstelle_mv=f"{mv.blatt} {mv.zelle}"))
    return pd.DataFrame(out).sort_values(["kennzahl", "kompetenz_id", "jahr"]).reset_index(drop=True)


def iqb_trend_mv(con) -> pd.DataFrame:
    """Vom IQB veröffentlichte Veränderungen (Globalskala), nicht selbst berechnet."""
    pruefe(con, "V_IQB24_KL9_ALLE", "V_IQB24_KL9_ALLE", "mittelwert", "zeit")
    return pd.read_sql("SELECT land_id, zeitpunkt_id, wert AS differenz, se FROM fact_aggregat "
                       "WHERE verfahren_id='V_IQB24_KL9_ALLE' AND kennzahl='differenz_mittelwert' "
                       "AND kompetenz_id='SEK1-0' AND land_id IN ('MV','DE') ORDER BY land_id, zeitpunkt_id", con)


def sperren_demo(con) -> list[tuple[str, str]]:
    """Versucht bewusst unzulässige Vergleiche und hält die Begründungen fest."""
    faelle = [("IQB Klasse 4 gegen IQB Klasse 9", "V_IQB21_KL4", "V_IQB24_KL9_ALLE", "mittelwert", "quelle"),
              ("Simulation gegen IQB Klasse 9", SIM_VERFAHREN, "V_IQB24_KL9_ALLE", "loesungsanteil", "quelle"),
              ("Schülerzahl Tabelle 04 gegen Tabelle 07", "V_DESTATIS_SCHUELER", "V_DESTATIS_WIEDERHOLER",
               "schueler_anzahl", "quelle"),
              ("Klassenzahl im Ländervergleich (nicht beantragt)", "V_DESTATIS_KLASSEN", "V_DESTATIS_KLASSEN",
               "klassen_anzahl", "land")]
    out = []
    for text, a, b, kz, dim in faelle:
        try:
            pruefe(con, a, b, kz, dim)
            raise RuntimeError(f"Sperre versagt: {text}")
        except NichtVergleichbar as e:
            out.append((text, str(e)))
    return out


def analysiere(con: sqlite3.Connection) -> dict:
    df = lade_sim(con)
    return dict(profil=kompetenzprofil(df), baender=baender(df), veraenderung=veraenderung(con, df),
                gruppen=gruppen(con, df), sicherheit=einstufungssicherheit(df), iqb=iqb_mv(con),
                iqb_trend=iqb_trend_mv(con), sperren=sperren_demo(con), sim=df)
