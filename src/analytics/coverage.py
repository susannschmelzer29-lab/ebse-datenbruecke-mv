"""Wie oft enthält das 95-%-Intervall der Veränderung den gesetzten Wert? (Wiederholte Simulation)

Läuft getrennt von run_all, weil es rund eine Minute dauert:  python -m src.analytics.coverage
"""
import numpy as np
import pandas as pd

from src.analytics.analysis import _bootstrap, wahre_veraenderung
from src.config import REPORTS
from src.transformation.simulate import saubere_daten

WIEDERHOLUNGEN = 100


def main() -> pd.DataFrame:
    wahr, treffer = wahre_veraenderung(), {l: 0 for l in wahre_veraenderung()}
    for s in range(WIEDERHOLUNGEN):
        d = saubere_daten(np.random.default_rng(1000 + s))
        d["prozent"] = 100 * d.punkte.astype(int) / d.max_punkte.astype(int)
        w = d.pivot_table(index=["kind_id", "schule_id", "leitidee"], columns="messzeitpunkt",
                          values="prozent").dropna().reset_index()
        w["diff"] = w.T2 - w.T1
        rng = np.random.default_rng(s)
        for l, g in w.groupby("leitidee"):
            _, u, o = _bootstrap(g, "diff", rng)
            treffer[l] += u <= wahr[l] <= o
    t = pd.DataFrame([dict(leitidee=l, wiederholungen=WIEDERHOLUNGEN, treffer=n,
                           ueberdeckung_prozent=100 * n / WIEDERHOLUNGEN) for l, n in treffer.items()])
    REPORTS.mkdir(exist_ok=True)
    t.to_csv(REPORTS / "SIM_ueberdeckung.csv", index=False, lineterminator="\n")
    return t


if __name__ == "__main__":
    print(main().to_string(index=False))
