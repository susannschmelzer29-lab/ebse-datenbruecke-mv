"""Vollständig künstliche Kompetenzdaten erzeugen, einschließlich dokumentierter Fehler.

Alle Schulen und Kinder sind erfunden. Die Parameter sind frei gesetzt und NICHT aus realen
Ergebnissen abgeleitet. Sie stehen in SIM_parameter.json, damit die Analyse prüfbar ist.
"""
import json

import numpy as np
import pandas as pd

from src.config import (ITEMS_JE_LEITIDEE, KLASSEN_JE_SCHULE, LEITIDEEN, N_KINDER, N_SCHULEN, SEED,
                        SIMULATED)

PARAMETER = {
    "hinweis": "SIMULIERT. Frei gesetzte Werte ohne Bezug zu realen Schulen oder Ergebnissen.",
    "seed": SEED,
    "basis_logit": {"L1": 0.45, "L2": 0.05, "L3": -0.25, "L4": 0.25, "L5": 0.10},
    "zuwachs_logit": {"L1": 0.45, "L2": 0.30, "L3": 0.50, "L4": 0.10, "L5": 0.25},
    "effekt_gesamtschule": 0.20,
    "effekt_staedtisch": 0.0,
    "sd_schule": 0.20, "sd_klasse": 0.15, "sd_kind": 0.80, "sd_kind_leitidee": 0.35, "sd_anlass": 0.25,
    "anteil_fehlend": {"T1": 0.02, "T2": 0.05},
}
FENSTER = {"T1": ("2025-09-08", "2025-09-26"), "T2": ("2026-09-07", "2026-09-25")}
KLASSENSTUFE = {"T1": 5, "T2": 6}

SPALTEN = ["sim_kennzeichen", "kind_id", "schule_id", "klasse_id", "schulart", "raumtyp", "messzeitpunkt",
           "klassenstufe", "leitidee", "testdatum", "punkte", "max_punkte", "ist_simuliert"]


def schulen() -> pd.DataFrame:
    return pd.DataFrame([dict(
        schule_id=f"SIM-S{i:02d}", name=f"Fiktive Schule {i:02d}",
        schulart="Gesamtschule" if i % 3 == 0 else "Regionale Schule",
        raumtyp="städtisch" if i % 2 == 0 else "ländlich") for i in range(1, N_SCHULEN + 1)])


def saubere_daten(rng) -> pd.DataFrame:
    p, s = PARAMETER, schulen()
    je_klasse = N_KINDER // (N_SCHULEN * KLASSEN_JE_SCHULE)
    zeilen, kind_nr = [], 0
    for sch in s.itertuples():
        mu_s = (rng.normal(0, p["sd_schule"]) + p["effekt_gesamtschule"] * (sch.schulart == "Gesamtschule")
                + p["effekt_staedtisch"] * (sch.raumtyp == "städtisch"))
        for k in range(KLASSEN_JE_SCHULE):
            mu_k, klasse = rng.normal(0, p["sd_klasse"]), f"{sch.schule_id}-{'ab'[k]}"
            for _ in range(je_klasse):
                kind_nr += 1
                theta = mu_s + mu_k + rng.normal(0, p["sd_kind"])
                profil = {l: rng.normal(0, p["sd_kind_leitidee"]) for l in LEITIDEEN}
                for t, (von, bis) in FENSTER.items():
                    fehlt = rng.random() < p["anteil_fehlend"][t]
                    tage = (pd.Timestamp(bis) - pd.Timestamp(von)).days
                    datum = pd.Timestamp(von) + pd.Timedelta(days=int(rng.integers(0, tage + 1)))
                    anlass = rng.normal(0, p["sd_anlass"])
                    for l in LEITIDEEN:
                        eta = theta + profil[l] + anlass + p["basis_logit"][l] + (
                            p["zuwachs_logit"][l] if t == "T2" else 0)
                        punkte = int(rng.binomial(ITEMS_JE_LEITIDEE, 1 / (1 + np.exp(-eta))))
                        if not fehlt:
                            zeilen.append(["SIMULIERT", f"SIM-K{kind_nr:04d}", sch.schule_id, klasse,
                                           sch.schulart, sch.raumtyp, t, KLASSENSTUFE[t], l,
                                           datum.strftime("%Y-%m-%d"), punkte, ITEMS_JE_LEITIDEE, 1])
    return pd.DataFrame(zeilen, columns=SPALTEN).astype(str)


def fehler_einbauen(sauber: pd.DataFrame, rng) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Baut bekannte Fehler ein. Liefert Rohdaten und das Protokoll (Zeile, Regel, Art)."""
    df, protokoll = sauber.copy(), []
    frei = list(rng.permutation(len(df)))

    def ziehe(n):
        return [int(frei.pop()) for _ in range(n)]

    def notiere(i, regel, art):
        protokoll.append(dict(roh_zeile=i + 2, regel_id=regel, art=art))  # +2: Kopfzeile, 1-basiert

    for i in ziehe(30):
        df.loc[i, "punkte"] = ""
        notiere(i, "DQ01", "Punktwert fehlt")
    for n, i in enumerate(ziehe(15)):
        df.loc[i, "punkte"] = ["27", "-1", "99"][n % 3]
        notiere(i, "DQ03", "Punkte außerhalb 0 bis 20")
    varianten = {"Regionale Schule": ["Reg. Schule", "regionale schule", "Regionalschule"],
                 "Gesamtschule": ["Ges.schule", "gesamtschule", "IGS"]}
    for n, i in enumerate(ziehe(40)):
        df.loc[i, "schulart"] = varianten[df.loc[i, "schulart"]][n % 3]
        notiere(i, "DQ04", "abweichende Schulartbezeichnung")
    for n, i in enumerate(ziehe(15)):
        df.loc[i, "testdatum"] = ["2026-02-31", "2062-09-10", "kein Datum"][n % 3]
        notiere(i, "DQ05", "ungültiges oder unmögliches Datum")
    for i in ziehe(10):
        df.loc[i, "kind_id"] = ""
        notiere(i, "DQ06", "Kind-ID fehlt")
    for i in ziehe(15):
        df.loc[i, "klassenstufe"] = {"5": "6", "6": "5"}[df.loc[i, "klassenstufe"]]
        notiere(i, "DQ07", "Klassenstufe passt nicht zum Messzeitpunkt")
    for n, i in enumerate(ziehe(40)):
        if n % 2:
            df.loc[i, "punkte"] = df.loc[i, "punkte"] + ",0"
        else:
            df.loc[i, "testdatum"] = pd.Timestamp(df.loc[i, "testdatum"]).strftime("%d.%m.%Y")
        notiere(i, "DQ08", "abweichendes Zahlen- oder Datumsformat")
    for n, i in enumerate(ziehe(10)):
        df.loc[i, "max_punkte" if n % 2 else "leitidee"] = ""
        notiere(i, "DQ09", "Metadatum fehlt")
    anhang = []
    for n, i in enumerate(ziehe(20)):
        kopie = df.loc[i].copy()
        if n >= 15:  # widersprüchliches Duplikat: beide Zeilen sind verdächtig
            kopie["punkte"] = str((int(kopie["punkte"]) + 5) % 21)
            notiere(i, "DQ02", "widersprüchliches Duplikat")
        anhang.append(kopie)
        protokoll.append(dict(roh_zeile=len(df) + len(anhang) + 1, regel_id="DQ02",
                              art="widersprüchliches Duplikat" if n >= 15 else "exaktes Duplikat"))
    roh = pd.concat([df, pd.DataFrame(anhang)], ignore_index=True)
    return roh, pd.DataFrame(protokoll).sort_values(["roh_zeile", "regel_id"]).reset_index(drop=True)


def simuliere() -> None:
    SIMULATED.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    roh, protokoll = fehler_einbauen(saubere_daten(rng), rng)
    opt = dict(index=False, encoding="utf-8", lineterminator="\n")
    roh.to_csv(SIMULATED / "SIM_ergebnisse_roh.csv", **opt)
    protokoll.to_csv(SIMULATED / "SIM_fehlerprotokoll.csv", **opt)
    schulen().to_csv(SIMULATED / "SIM_schulen.csv", **opt)
    (SIMULATED / "SIM_parameter.json").write_text(
        json.dumps(PARAMETER, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
