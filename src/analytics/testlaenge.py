"""SIMULIERT: Wie sicher ist die Einstufung in Bänder bei 10 bis 100 Aufgaben?

Eigenständiges Experiment, verändert den Hauptlauf nicht:  python -m src.analytics.testlaenge
Es nutzt dieselben Parameter wie die Simulation (Beginn Klasse 6), aber viele fiktive Kinder,
damit die Anteile kaum vom Zufall abhängen. Der wahre Lösungsanteil je Kind ist hier bekannt.
"""
import numpy as np
import pandas as pd

from src.analytics.analysis import GRENZEN, wilson
from src.config import LEITIDEEN, REPORTS, SEED
from src.transformation.simulate import PARAMETER as P

LAENGEN = [10, 20, 40, 60, 100]
N = 40_000


def wahre_anteile(rng, n=N) -> np.ndarray:
    """Wahrer Lösungsanteil je Kind und Leitidee zu Beginn Klasse 6."""
    sd = np.sqrt(P["sd_schule"] ** 2 + P["sd_klasse"] ** 2 + P["sd_kind"] ** 2)
    theta = rng.normal(0, sd, (n, 1)) + P["effekt_gesamtschule"] * (rng.random((n, 1)) < 1 / 3)
    theta = theta + rng.normal(0, P["sd_anlass"], (n, 1)) + rng.normal(0, P["sd_kind_leitidee"], (n, len(LEITIDEEN)))
    basis = np.array([P["basis_logit"][l] + P["zuwachs_logit"][l] for l in LEITIDEEN])
    return 1 / (1 + np.exp(-(theta + basis)))


def stufe(prozent) -> np.ndarray:
    return np.digitize(prozent, GRENZEN)


def kennwerte(punkte, aufgaben, wahr) -> dict:
    u, o = wilson(punkte, aufgaben)
    unsicher = np.logical_or.reduce([(u < g) & (o >= g) for g in GRENZEN])
    abstand = np.abs(stufe(100 * punkte / aufgaben) - stufe(100 * wahr))
    sicher = ~unsicher
    return dict(aufgaben=aufgaben, unsicher_prozent=100 * unsicher.mean(),
                falsch_prozent=100 * (abstand > 0).mean(), zwei_baender_falsch_prozent=100 * (abstand > 1).mean(),
                falsch_wenn_sicher_prozent=100 * (abstand[sicher] > 0).mean() if sicher.any() else np.nan,
                halbe_intervallbreite=float(((o - u) / 2).mean()))


def je_leitidee() -> pd.DataFrame:
    rng = np.random.default_rng(SEED + 10)
    wahr = wahre_anteile(rng)
    return pd.DataFrame([kennwerte(rng.binomial(n, wahr), n, wahr) for n in LAENGEN])


def gesamttest() -> pd.DataFrame:
    """Alle fünf Leitideen zusammen: eine Aussage je Kind statt fünf."""
    rng = np.random.default_rng(SEED + 11)
    wahr, k = wahre_anteile(rng), len(LEITIDEEN)
    out = []
    for n in LAENGEN:
        d = kennwerte(rng.binomial(n, wahr).sum(1), n * k, wahr.mean(1))
        out.append({"aufgaben_je_leitidee": n} | d)
    return pd.DataFrame(out)


def main() -> None:
    a, b = je_leitidee(), gesamttest()
    REPORTS.mkdir(exist_ok=True)
    opt = dict(index=False, lineterminator="\n", float_format="%.2f")
    a.to_csv(REPORTS / "SIM_testlaenge_je_leitidee.csv", **opt)
    b.to_csv(REPORTS / "SIM_testlaenge_gesamt.csv", **opt)
    print(a.round(1).to_string(index=False))
    print(b.round(1).to_string(index=False))


if __name__ == "__main__":
    main()
