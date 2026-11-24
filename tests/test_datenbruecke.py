"""Automatisierte Tests. Start: python -m pytest

Tests mit realen Quellen brauchen die Rohdateien (python -m src.ingestion.fetch) und werden sonst übersprungen.
"""
import json
import re
import sqlite3

import numpy as np
import pandas as pd
import pytest

from src.analytics import analysis
from src.config import MIN_GRUPPE, QUELLEN, QUERIES, RAW, ROOT, SCHEMA, band
from src.ingestion import fetch, parse_real
from src.quality import checks
from src.run_all import verarbeite
from src.transformation import normalize, simulate
from src.transformation.compare import NichtVergleichbar, pruefe, vergleiche

ROHDATEN = all((RAW / q["datei"]).exists() for q in QUELLEN.values())
real = pytest.mark.skipif(not ROHDATEN, reason="Rohdateien fehlen")


@pytest.fixture(scope="session")
def lauf(tmp_path_factory):
    if not ROHDATEN:
        pytest.skip("Rohdateien fehlen")
    return verarbeite(tmp_path_factory.mktemp("db") / "test.sqlite", log=lambda *_: None)


def fakt(con, **k):
    wo = " AND ".join(f"{a} = ?" for a in k)
    z = con.execute(f"SELECT fakt_id FROM fact_aggregat WHERE {wo}", tuple(k.values())).fetchall()
    assert len(z) == 1, (k, len(z))
    return z[0][0]


# ------------------------------------------------------------ Rohdaten und Import
@real
def test_rohdaten_stimmen_mit_manifest():
    for qid, m in fetch.lade_manifest().items():
        fetch.pruefe_datei(RAW / QUELLEN[qid]["datei"], m["sha256"])


def test_veraenderte_rohdatei_wird_erkannt(tmp_path):
    p = tmp_path / "x.xlsx"
    p.write_bytes(b"PK veraendert")
    with pytest.raises(fetch.RohdatenFehler):
        fetch.pruefe_datei(p, "0" * 64)


def test_unbekannte_rohdatei_wird_nicht_zur_referenz(tmp_path, monkeypatch):
    monkeypatch.setattr(fetch, "RAW", tmp_path)
    monkeypatch.setattr(fetch, "MANIFEST", tmp_path / "manifest.json")
    (tmp_path / QUELLEN["Q1"]["datei"]).write_bytes(b"PK fremd")
    with pytest.raises(fetch.RohdatenFehler, match="Herkunft"):
        fetch.fetch_all(log=lambda *_: None)


@real
def test_verarbeitung_veraendert_rohdaten_nicht(lauf):
    for qid, m in fetch.lade_manifest().items():
        assert fetch.sha256(RAW / QUELLEN[qid]["datei"]) == m["sha256"]


def test_spaltenvertrag_bricht_bei_falschem_kopf_ab():
    with pytest.raises(parse_real.VertragFehler):
        parse_real._erwarte("SD", "SE", "Test")


@real
def test_stichproben_gegen_originalzellen(lauf):
    """Von Hand in den Originaldateien abgelesene Werte."""
    con = lauf["con"]
    q = "SELECT wert, se FROM fact_aggregat WHERE fakt_id = ?"
    a = fakt(con, verfahren_id="V_IQB24_KL9_ALLE", land_id="MV", kompetenz_id="SEK1-0", zeitpunkt_id="2024", kennzahl="mittelwert")
    assert con.execute(q, (a,)).fetchone() == (471.0, 2.6)
    b = fakt(con, verfahren_id="V_IQB24_KL9_ZIELGLEICH", land_id="MV", kompetenz_id="SEK1-0", zeitpunkt_id="2024", kennzahl="ms_msa_verfehlt")
    assert con.execute(q, (b,)).fetchone() == (33.8, 1.4)
    c = fakt(con, verfahren_id="V_IQB24_KL9_ALLE", land_id="MV", kompetenz_id="SEK1-0", zeitpunkt_id="2018-2012", kennzahl="differenz_mittelwert")
    assert con.execute(q, (c,)).fetchone() == (-23.0, 4.9)


@real
def test_jeder_reale_wert_hat_fundstelle(lauf):
    n, ohne = lauf["con"].execute("SELECT COUNT(*), SUM(blatt = '' OR zelle = '' OR sha256 IS NULL) FROM v_lineage").fetchone()
    assert n > 3900 and ohne == 0


# ------------------------------------------------------------ Transformation
def test_tausenderpunkt_wird_nicht_als_dezimalpunkt_gelesen():
    assert normalize.zahl("15.248", "Q4") == 15248
    assert normalize.zahl("15.248", "Q1") == 15.248
    with pytest.raises(ValueError):
        normalize.zahl("15,2", "Q4")


def test_gleitkommarest_wird_bereinigt():
    assert normalize.zahl("28.999999999999996", "Q2") == 29.0


def test_unbekanntes_land_bricht_ab():
    assert normalize.land("Mecklenburg-Vormpommern") == "Mecklenburg-Vorpommern"
    with pytest.raises(ValueError):
        normalize.land("Mecklenburg")


@pytest.mark.parametrize("p, name", [(0, "Unterstützung prüfen"), (49.99, "Unterstützung prüfen"), (50, "im Aufbau"),
                                     (74.99, "im Aufbau"), (75, "sicher"), (100, "sicher")])
def test_bandgrenzen(p, name):
    assert band(p) == name


# ------------------------------------------------------------ Datenqualität
@real
def test_bekannte_reale_faelle_werden_gefunden(lauf):
    b = pd.DataFrame(lauf["befunde_real"])
    assert (b.regel_id == "DQ03").sum() == 8
    assert (b[b.regel_id == "DQ04"].rohwert == "Mecklenburg-Vormpommern").sum() == 54
    assert "Niedersachen" in set(b[b.regel_id == "DQ04"].rohwert)
    assert b[(b.regel_id == "DQ11") & (b.quelle_id == "Q3")].meldung.str.contains("Mecklenburg").all()
    assert (b[b.regel_id == "DQ12"].meldung == "Differenz entspricht genau Förder- und Waldorfschulen").sum() == 2
    assert ((b.regel_id == "DQ11") & b.meldung.str.contains("662")).sum() == 1
    assert (b.regel_id == "DQ10").sum() == 0


@real
def test_quellenabgleich_schlaegt_bei_abweichung_an(lauf):
    df = lauf["real"].copy()
    i = df.index[(df.quelle_id == "Q4") & (df.schulart_roh == "Gymnasium")][0]
    df.loc[i, "wert_roh"] = "690"
    assert sum(x["regel_id"] == "DQ10" for x in checks.pruefe_real(df)) == 1


@real
def test_negativer_standardfehler_wird_verworfen_wert_bleibt(lauf):
    z = lauf["con"].execute("SELECT wert, se, se_roh FROM fact_aggregat WHERE status = 'se_verworfen'").fetchall()
    assert len(z) == 8 and all(w is not None and se is None and r.startswith("-") for w, se, r in z)


@real
def test_eingebaute_fehler_werden_alle_erkannt(lauf):
    t = lauf["leistung"]
    assert t.eingebaut.sum() == 200 and t.uebersehen.sum() == 0 and t.fehlalarm.sum() == 0
    assert set(t.regel_id) == {f"DQ0{i}" for i in range(1, 10)}


@real
def test_kein_datensatz_verschwindet_stillschweigend(lauf):
    ausgeschlossen = set(range(2, len(lauf["roh"]) + 2)) - set(lauf["sauber"].roh_zeile)
    begruendet = {b["roh_zeile"] for b in lauf["befunde_sim"] if b["behandlung"] == checks.AUSSCHLUSS}
    assert ausgeschlossen == begruendet


def test_fehlende_simulationskennzeichnung_bricht_ab():
    rng = np.random.default_rng(1)
    roh = simulate.saubere_daten(rng).head(3)
    roh.loc[0, "sim_kennzeichen"] = ""
    with pytest.raises(ValueError, match="simuliert"):
        checks.pruefe_sim(roh)


# ------------------------------------------------------------ Datenmodell und Vergleichssperre
def test_schema_verhindert_unmarkierte_simulation_und_negative_fehler():
    con = sqlite3.connect(":memory:")
    con.executescript(SCHEMA.read_text(encoding="utf-8"))
    con.execute("PRAGMA foreign_keys = OFF")
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO fact_simulation VALUES (1,'V','SIM-K1','T1',5,'L1','2025-09-10',10,20,'im Aufbau',2,0)")
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO sim_schule VALUES ('SIM-S99','Echte Schule','Regionale Schule','ländlich')")
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO fact_aggregat VALUES (1,'Q','V','MV',9,NULL,NULL,'2024','x',1,-1,'gueltig',NULL,'1','-1','MV','b','z')")


@real
def test_erlaubter_vergleich(lauf):
    con, k = lauf["con"], dict(verfahren_id="V_IQB24_KL9_ALLE", kompetenz_id="SEK1-0", zeitpunkt_id="2024", kennzahl="mittelwert")
    v = vergleiche(con, fakt(con, land_id="DE", **k), fakt(con, land_id="MV", **k))
    assert v["regel"] == "F3" and v["differenz"] == -3


@real
def test_unzulaessige_vergleiche_werden_abgewiesen(lauf):
    con = lauf["con"]
    k9 = fakt(con, verfahren_id="V_IQB24_KL9_ALLE", land_id="DE", kompetenz_id="SEK1-0", zeitpunkt_id="2024", kennzahl="mittelwert")
    k4 = fakt(con, verfahren_id="V_IQB21_KL4", land_id="DE", kompetenz_id="PRIM-0", zeitpunkt_id="2021", kennzahl="mittelwert")
    mv = fakt(con, verfahren_id="V_IQB21_KL4", land_id="MV", kompetenz_id="PRIM-0", zeitpunkt_id="2021", kennzahl="mittelwert")
    for a, b, grund in ((k9, k4, "Klassenstufen"), (k4, mv, "nicht ausgewiesen"), (k9, k9, "genau eine Dimension")):
        with pytest.raises(NichtVergleichbar, match=grund):
            vergleiche(con, a, b)
    assert len(analysis.sperren_demo(con)) == 4


@real
def test_nicht_freigegebene_regel_sperrt(lauf):
    con = lauf["con"]
    con.execute("UPDATE vergleichsregel SET status = 'vorgeschlagen' WHERE regel_id = 'F6'")
    try:
        with pytest.raises(NichtVergleichbar, match="noch nicht freigegeben"):
            analysis.veraenderung(con, analysis.lade_sim(con))
    finally:
        con.rollback()
    assert pruefe(con, "V_SIM_MATHE_OS", "V_SIM_MATHE_OS", "loesungsanteil", "zeit") == "F6"


@real
def test_simulation_und_reale_daten_sind_getrennt(lauf):
    con = lauf["con"]
    assert con.execute("SELECT COUNT(*) FROM fact_aggregat f JOIN dim_verfahren v USING (verfahren_id) WHERE v.ist_simuliert = 1").fetchone()[0] == 0
    assert con.execute("SELECT COUNT(*) FROM fact_simulation f JOIN dim_verfahren v USING (verfahren_id) WHERE v.ist_simuliert = 0").fetchone()[0] == 0
    for py in (ROOT / "src").rglob("*.py"):
        for sql in re.findall(r'"""(.*?)"""|"([^"\n]*)"', py.read_text(encoding="utf-8"), re.S):
            text = " ".join(sql)
            assert not (re.search(r"(FROM|JOIN)\s+fact_aggregat", text) and re.search(r"(FROM|JOIN)\s+(fact_simulation|v_simulation)", text)), py


@real
def test_beispielabfragen_laufen(lauf):
    sql = re.sub(r"--.*", "", QUERIES.read_text(encoding="utf-8"))
    abfragen = [q for q in sql.split(";") if q.strip()]
    assert len(abfragen) >= 6
    for q in abfragen:
        assert lauf["con"].execute(q).fetchall(), q


# ------------------------------------------------------------ Analyse und Reproduzierbarkeit
@real
def test_kompetenzprofil_gegen_direktes_sql(lauf):
    df = analysis.lade_sim(lauf["con"])
    p = analysis.kompetenzprofil(df).set_index(["zeitpunkt", "leitidee"]).mittel
    for t, l, m in lauf["con"].execute("SELECT zeitpunkt_id, kompetenz_id, SUM(100.0 * punkte / max_punkte) / COUNT(*) FROM fact_simulation GROUP BY 1, 2"):
        assert p[(t, l)] == pytest.approx(m)


@real
def test_bandanteile_ergeben_100(lauf):
    b = analysis.baender(analysis.lade_sim(lauf["con"]))
    assert np.allclose(b.groupby(["zeitpunkt_id", "kompetenz_id"]).anteil.sum(), 100)


@real
def test_kleine_gruppen_werden_unterdrueckt(lauf):
    df = analysis.lade_sim(lauf["con"])
    klein = df[df.schulart == "Gesamtschule"].kind_id.unique()[MIN_GRUPPE - 1:]
    g = analysis.gruppen(lauf["con"], df[~df.kind_id.isin(klein)]).set_index("merkmal")
    assert bool(g.loc["schulart", "unterdrueckt"]) and pd.isna(g.loc["schulart", "diff"])


def test_wilson_bekannter_wert():
    u, o = analysis.wilson(10, 20)
    assert u == pytest.approx(29.93, abs=0.01) and o == pytest.approx(70.07, abs=0.01)


@real
def test_zwei_laeufe_sind_identisch(lauf, tmp_path):
    zwei = verarbeite(tmp_path / "b.sqlite", log=lambda *_: None)
    assert list(lauf["con"].iterdump()) == list(zwei["con"].iterdump())
    zwei["con"].close()


def test_parameterdatei_ist_als_simuliert_markiert():
    simulate.simuliere()
    p = json.loads((simulate.SIMULATED / "SIM_parameter.json").read_text(encoding="utf-8"))
    assert p["hinweis"].startswith("SIMULIERT")
    assert all(f.name.startswith("SIM_") for f in simulate.SIMULATED.iterdir() if f.suffix in (".csv", ".json"))
