"""SQLite-Datenbank vollständig neu aufbauen."""
import sqlite3

import pandas as pd

from src.config import DB, LEITIDEEN, PROCESSED, QUELLEN, SCHEMA, SIMULATED
from src.ingestion.parse_real import q3_hinweis_mv
from src.quality.checks import REGELN as DQ_REGELN
from src.transformation import normalize
from src.transformation.rules import REGELN, VERFAHREN

RAHMEN = {"Q2": ("SEK1", "IQB Sekundarstufe I (Bildungstrend 2024)"),
          "Q3": ("PRIM", "IQB Primarstufe (Bildungstrend 2021)")}


def _zeitpunkt_art(z: str) -> tuple[str, str]:
    if "/" in z:
        return "Schuljahr", f"Schuljahr {z}"
    if "-" in z:
        return "Differenz", f"Veränderung {z.split('-')[1]} bis {z.split('-')[0]}"
    return "Erhebungsjahr", f"Erhebung {z}"


def baue(real: pd.DataFrame, sim: pd.DataFrame, befunde: list[dict], manifest: dict, pfad=DB) -> sqlite3.Connection:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    pfad.unlink(missing_ok=True)
    con = sqlite3.connect(pfad)
    con.executescript(SCHEMA.read_text(encoding="utf-8"))
    con.execute("PRAGMA foreign_keys = ON")

    for qid, q in QUELLEN.items():
        m = manifest[qid]
        con.execute("INSERT INTO dim_datenquelle VALUES (?,?,?,?,?,?,?,?,?,?,?,0)",
                    (qid, q["titel"], q["herausgeber"], q["bezugsjahr"], q["raum"], q["datenart"], q["lizenz"],
                     q["url"], q["datei"], m["sha256"], m["abgerufen_utc"]))
    con.execute("INSERT INTO dim_datenquelle VALUES ('SIM','Simulierte Kompetenzdaten Mathematik 5/6',"
                "'Eigene Simulation','fiktiv 2025/2026','fiktiv','SIMULIERT, Individualdaten',"
                "'eigene Daten',NULL,'SIM_ergebnisse_roh.csv',NULL,NULL,1)")
    con.executemany("INSERT INTO dim_verfahren VALUES (?,?,?,?,?,?)", VERFAHREN)
    con.executemany("INSERT INTO dim_land VALUES (?,?)", normalize.LAENDER.items())
    con.executemany("INSERT INTO dim_kompetenz VALUES (?,?,?)",
                    [(k, "Rahmenplan Mathematik M-V 2026, Orientierungsstufe", v) for k, v in LEITIDEEN.items()])
    con.executemany("INSERT INTO dq_regel VALUES (?,?,?,?)", DQ_REGELN)
    con.executemany("INSERT INTO vergleichsregel VALUES (?,?,?,?,?,?,?,?)", REGELN)

    zp = {z: _zeitpunkt_art(z) for z in sorted(real.zeitpunkt.unique())}
    zp |= {"T1": ("Messzeitpunkt", "SIMULIERT: Beginn Klasse 5"), "T2": ("Messzeitpunkt", "SIMULIERT: Beginn Klasse 6")}
    con.executemany("INSERT INTO dim_zeitpunkt VALUES (?,?,?)", [(z, *v) for z, v in zp.items()])

    sf = {}
    for q, s in real[real.schulart_roh.notna()][["quelle_id", "schulart_roh"]].drop_duplicates().itertuples(index=False):
        cur = con.execute("INSERT INTO dim_schulform (quelle_id, bezeichnung, harmonisiert_mv) VALUES (?,?,?)",
                          (q, s, normalize.SCHULFORM_MV.get((q, s))))
        sf[(q, s)] = cur.lastrowid
    komp = {}
    for q, (kuerzel, rahmen) in RAHMEN.items():
        for i, k in enumerate(real[real.quelle_id == q].kompetenz_roh.drop_duplicates()):
            komp[(q, k)] = f"{kuerzel}-{i}"
            con.execute("INSERT INTO dim_kompetenz VALUES (?,?,?)", (f"{kuerzel}-{i}", rahmen, k))

    zeilen = []
    for z in real.itertuples():
        wert = normalize.zahl(z.wert_roh, z.quelle_id)
        se = normalize.zahl(z.se_roh, z.quelle_id) if isinstance(z.se_roh, str) else None
        status, grund = "gueltig", None
        if se is not None and se < 0:
            se, status, grund = None, "se_verworfen", "Negativer Standardfehler in der Quelle"
        zeilen.append((z.quelle_id, z.verfahren_id, normalize.LAND_ID[normalize.land(z.land_roh)], int(z.klassenstufe),
                       sf.get((z.quelle_id, z.schulart_roh)), komp.get((z.quelle_id, z.kompetenz_roh)),
                       z.zeitpunkt, z.kennzahl, wert, se, status, grund, z.wert_roh,
                       z.se_roh if isinstance(z.se_roh, str) else None, z.land_roh, z.blatt, z.zelle))
    ort, hinweis = q3_hinweis_mv()
    for (q, _), kid in komp.items():
        if q == "Q3":
            for kz in ("mittelwert", "ms_verfehlt"):
                zeilen.append(("Q3", "V_IQB21_KL4", "MV", 4, None, kid, "2021", kz, None, None, "nicht_ausgewiesen",
                               hinweis, None, None, None, "Inhalt", ort))
    con.executemany(
        "INSERT INTO fact_aggregat (quelle_id, verfahren_id, land_id, klassenstufe, schulform_id, kompetenz_id, "
        "zeitpunkt_id, kennzahl, wert, se, status, statusgrund, wert_roh, se_roh, land_roh, blatt, zelle) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", zeilen)

    schulen = pd.read_csv(SIMULATED / "SIM_schulen.csv")
    con.executemany("INSERT INTO sim_schule VALUES (?,?,?,?)", schulen.itertuples(index=False, name=None))
    kinder = sim[["kind_id", "schule_id", "klasse_id"]].drop_duplicates().sort_values("kind_id")
    con.executemany("INSERT INTO sim_kind VALUES (?,?,?)", kinder.itertuples(index=False, name=None))
    con.executemany(
        "INSERT INTO fact_simulation (verfahren_id, kind_id, zeitpunkt_id, klassenstufe, kompetenz_id, testdatum, "
        "punkte, max_punkte, roh_zeile) VALUES ('V_SIM_MATHE_OS',?,?,?,?,?,?,?,?)",
        [(z.kind_id, z.zeitpunkt_id, z.klassenstufe, z.kompetenz_id, z.testdatum, z.punkte, z.max_punkte,
          z.roh_zeile) for z in sim.itertuples()])
    con.executemany(
        "INSERT INTO dq_befund (regel_id, quelle_id, fundstelle, feld, rohwert, meldung, behandlung) "
        "VALUES (:regel_id,:quelle_id,:fundstelle,:feld,:rohwert,:meldung,:behandlung)", befunde)
    con.commit()
    verletzt = con.execute("PRAGMA foreign_key_check").fetchall()
    if verletzt:
        raise RuntimeError(f"Fremdschlüssel verletzt: {verletzt[:3]}")
    return con
