"""Gesamtlauf: Abruf, Simulation, Qualitätsprüfung, Datenbank, Analyse, Berichte.

    python -m src.run_all
"""
import sys

import pandas as pd

from src.analytics.analysis import analysiere
from src.config import DB, PROCESSED, SIMULATED
from src.ingestion.fetch import fetch_all
from src.ingestion.parse_real import parse_all
from src.quality import checks
from src.reporting import charts, dashboard, report
from src.transformation.build_db import baue
from src.transformation.simulate import simuliere


def verarbeite(db=DB, log=print):
    """Alles bis einschließlich Datenbank. Wird auch von den Tests genutzt."""
    manifest = fetch_all(log)
    real = parse_all()
    simuliere()
    roh = pd.read_csv(SIMULATED / "SIM_ergebnisse_roh.csv", dtype=str, keep_default_na=False)
    protokoll = pd.read_csv(SIMULATED / "SIM_fehlerprotokoll.csv")
    befunde_real = checks.pruefe_real(real)
    befunde_sim, sauber = checks.pruefe_sim(roh)
    con = baue(real, sauber, befunde_real + befunde_sim, manifest, db)
    return dict(con=con, real=real, roh=roh, sauber=sauber, befunde_real=befunde_real, befunde_sim=befunde_sim,
                leistung=checks.erkennungsleistung(befunde_sim, protokoll), abgleich=checks.quellenabgleich(real))


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print("1/4 Rohdaten abrufen und prüfen")
    e = verarbeite()
    e["real"].to_csv(PROCESSED / "real_mit_fundstelle.csv", index=False, encoding="utf-8", lineterminator="\n")
    print(f"2/4 Datenbank: {len(e['real'])} reale Werte, {len(e['sauber'])} von {len(e['roh'])} simulierten Zeilen")
    print(f"    Befunde: {len(e['befunde_real'])} real, {len(e['befunde_sim'])} simuliert")
    print("3/4 Analyse und Grafiken")
    r = analysiere(e["con"])
    charts.alle(r)
    print("4/4 Berichte")
    n_real = e["real"].quelle_id.value_counts().to_dict()
    report.schreibe(e["con"], r, e["leistung"], e["abgleich"], n_real, len(e["roh"]), len(e["sauber"]))
    dashboard.schreibe(e["con"], r, e["abgleich"], n_real)
    e["con"].close()
    print("Fertig. Öffnen: dashboard/dashboard.html (interaktiv) oder dashboard/index.html (Bericht)")


if __name__ == "__main__":
    main()
