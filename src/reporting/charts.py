"""Grafiken. Jede Grafik mit simulierten Daten trägt den Vermerk SIMULIERT."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.config import BAENDER, LEITIDEEN, REPORTS

FL, TXT, TXT2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLAU, ORANGE = "#2a78d6", "#eb6834"
STUFEN = dict(zip([b for _, b in BAENDER], ["#86b6ef", "#2a78d6", "#104281"]))
STUFEN_TEXT = dict(zip([b for _, b in BAENDER], [TXT, "#ffffff", "#ffffff"]))
ORDNER = REPORTS / "grafiken"
SIM = "SIMULIERTE DATEN, keine Aussage über reale Kinder oder Schulen"
NAMEN = {l: f"{l}  {n}".replace("Strukturen und funktionaler Zusammenhang", "Strukturen und funkt. Zus.")
         for l, n in LEITIDEEN.items()}
L = list(LEITIDEEN)

plt.rcParams.update({
    "figure.facecolor": FL, "axes.facecolor": FL, "savefig.facecolor": FL, "font.size": 10,
    "font.family": "DejaVu Sans", "axes.edgecolor": GRID, "axes.labelcolor": TXT2, "text.color": TXT,
    "xtick.color": TXT2, "ytick.color": TXT, "axes.spines.top": False, "axes.spines.right": False,
    "axes.spines.left": False, "axes.grid": True, "axes.axisbelow": True, "grid.color": GRID,
    "grid.linewidth": 0.8, "ytick.major.size": 0, "xtick.major.size": 0, "svg.hashsalt": "ebse"})


def _fertig(fig, name, titel, vermerk):
    fig.suptitle(titel, x=0.02, y=0.985, ha="left", fontsize=12, fontweight="bold")
    fig.text(0.02, 0.015, vermerk, ha="left", fontsize=8, color=TXT2)
    fig.tight_layout(rect=(0, 0.045, 1, 0.94))
    ORDNER.mkdir(parents=True, exist_ok=True)
    fig.savefig(ORDNER / f"{name}.png", dpi=140, metadata={"Software": None})
    plt.close(fig)


def _pos():
    return np.arange(len(L))[::-1]


def profil(t):
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    y = _pos()
    for zp, f, off, name in (("T1", BLAU, 0.13, "Beginn Klasse 5"), ("T2", ORANGE, -0.13, "Beginn Klasse 6")):
        g = t[t.zeitpunkt == zp].set_index("leitidee").loc[L]
        ax.errorbar(g.mittel, y + off, xerr=[g.mittel - g.ki_u, g.ki_o - g.mittel], fmt="o", ms=8, color=f,
                    lw=2, capsize=0, label=name, mec=FL, mew=1.5)
        for yy, m, o in zip(y + off, g.mittel, g.ki_o):
            ax.text(o + 0.7, yy, f"{m:.0f}", va="center", fontsize=9, color=TXT2)
    ax.set_yticks(y, [NAMEN[l] for l in L])
    ax.set_xlim(35, 80)
    ax.set_ylim(-0.9, len(L) - 0.5)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("mittlerer Lösungsanteil in Prozent (Achse beginnt bei 35), Punkt mit 95-%-Intervall")
    ax.legend(frameon=False, loc="lower right")
    _fertig(fig, "1_kompetenzprofil", "Kompetenzprofil nach Leitidee", SIM)


def baender(t):
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 4.2), sharey=True)
    y = _pos()
    for ax, zp, titel in zip(axs, ("T1", "T2"), ("Beginn Klasse 5", "Beginn Klasse 6")):
        links = np.zeros(len(L))
        for b, f in STUFEN.items():
            w = t[(t.zeitpunkt_id == zp) & (t.band == b)].set_index("kompetenz_id").anteil.reindex(L, fill_value=0).to_numpy()
            ax.barh(y, w, left=links, color=f, height=0.55, label=b, edgecolor=FL, linewidth=2)
            for yy, x0, v in zip(y, links, w):
                if v >= 8:
                    ax.text(x0 + v / 2, yy, f"{v:.0f}", ha="center", va="center", fontsize=9, color=STUFEN_TEXT[b])
            links += w
        ax.set_title(titel, loc="left", fontsize=10, color=TXT2)
        ax.set_xlim(0, 100)
        ax.grid(axis="y", visible=False)
        ax.set_xlabel("Anteil in Prozent")
    axs[0].set_yticks(y, [NAMEN[l] for l in L])
    h, lab = axs[0].get_legend_handles_labels()
    fig.legend(h, lab, frameon=False, ncol=3, loc="upper right", bbox_to_anchor=(0.99, 0.945), fontsize=9)
    _fertig(fig, "2_baender", "Verteilung auf die drei Demonstrationsbänder", SIM + ". Keine amtlichen Kompetenzstufen.")


def verteilung(df):
    k = df.groupby(["kind_id", "zeitpunkt_id"]).agg(p=("prozent", "mean"), n=("kompetenz_id", "nunique")).reset_index()
    k = k[k.n == len(L)]
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.6), sharey=True, sharex=True)
    for ax, zp, titel, f in zip(axs, ("T1", "T2"), ("Beginn Klasse 5", "Beginn Klasse 6"), (BLAU, ORANGE)):
        w = k[k.zeitpunkt_id == zp].p
        ax.hist(w, bins=np.arange(0, 101, 10), color=f, edgecolor=FL, linewidth=2)
        ax.axvline(w.median(), color=TXT, lw=1.2, ls="--")
        ax.text(w.median() + 1.5, ax.get_ylim()[1] * 0.96, f"Median {w.median():.0f}", fontsize=9, va="top",
                bbox=dict(facecolor=FL, edgecolor="none", pad=1.5))
        ax.set_title(f"{titel} (n = {len(w)})", loc="left", fontsize=10, color=TXT2)
        ax.grid(axis="x", visible=False)
        ax.set_xlabel("Lösungsanteil über alle Leitideen in Prozent")
    axs[0].set_ylabel("Anzahl fiktiver Kinder")
    _fertig(fig, "3_verteilung", "Häufigkeitsverteilung der Gesamtergebnisse", SIM + ". Nur vollständige Profile.")


def veraenderung(t):
    fig, ax = plt.subplots(figsize=(8.6, 4.0))
    g, y = t.set_index("leitidee").loc[L], _pos()
    ax.axvline(0, color=TXT2, lw=1)
    ax.errorbar(g["diff"], y, xerr=[g["diff"] - g.ki_u, g.ki_o - g["diff"]], fmt="o", ms=8, lw=2, color=BLAU,
                mec=FL, mew=1.5, label="geschätzt, 95-%-Intervall")
    ax.scatter(g.gesetzt, y, marker="|", s=260, color=ORANGE, lw=2.5, zorder=4, label="in der Simulation gesetzt")
    for yy, d, o, w in zip(y, g["diff"], g.ki_o, g.gesetzt):
        ax.text(max(o, w) + 0.3, yy, f"+{d:.1f}".replace(".", ","), va="center", fontsize=9, color=TXT2)
    ax.set_yticks(y, [NAMEN[l] for l in L])
    ax.set_xlim(-1, 14)
    ax.set_ylim(-0.9, len(L) - 0.5)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Veränderung in Prozentpunkten, dieselben Kinder")
    ax.legend(frameon=False, loc="lower right", fontsize=9)
    _fertig(fig, "4_veraenderung", "Veränderung von Beginn Klasse 5 zu Beginn Klasse 6", SIM)


def gruppen(t):
    g = t[~t.unterdrueckt]
    fig, ax = plt.subplots(figsize=(8.6, 2.9))
    y = np.arange(len(g))[::-1]
    ax.axvline(0, color=TXT2, lw=1)
    ax.errorbar(g["diff"], y, xerr=[g["diff"] - g.ki_u, g.ki_o - g["diff"]], fmt="o", ms=8, lw=2, color=BLAU, mec=FL, mew=1.5)
    for yy, d, o in zip(y, g["diff"], g.ki_o):
        ax.text(o + 0.4, yy, f"{d:+.1f}".replace(".", ","), va="center", fontsize=9, color=TXT2)
    ax.set_yticks(y, [f"{a} minus {b}\n({sa} gegen {sb} Schulen)" for a, b, sa, sb in
                      zip(g.gruppe_a, g.gruppe_b, g.schulen_a, g.schulen_b)])
    ax.set_xlim(-12, 14)
    ax.set_ylim(-0.6, len(g) - 0.4)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Unterschied in Prozentpunkten, Beginn Klasse 6, 95-%-Intervall")
    _fertig(fig, "5_gruppen", "Gruppenunterschiede: beide Intervalle schließen null ein", SIM + ". Beschreibend, nicht kausal.")


def sicherheit(t):
    g = t[t.zeitpunkt_id == "T2"].set_index("kompetenz_id").loc[L]
    fig, ax = plt.subplots(figsize=(8.6, 3.6))
    y = _pos()
    ax.barh(y, g.anteil, color=BLAU, height=0.5)
    for yy, v in zip(y, g.anteil):
        ax.text(v + 1, yy, f"{v:.0f}", va="center", fontsize=9, color=TXT2)
    ax.set_yticks(y, [NAMEN[l] for l in L])
    ax.set_xlim(0, 100)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Anteil der Kinder in Prozent, deren 95-%-Bereich mindestens eine Bandgrenze enthält")
    _fertig(fig, "6_einstufungssicherheit", "Bei 20 Aufgaben schließt der Test das Nachbarband meist nicht aus", SIM)


def iqb(t):
    g = t[(t.kennzahl == "mittelwert") & (t.kompetenz_id == "SEK1-0")]
    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    for sp, f, name, dy in (("de", BLAU, "Deutschland", 9), ("mv", ORANGE, "Mecklenburg-Vorpommern", -15)):
        x = g.jahr + (0.12 if sp == "mv" else -0.12)
        ax.errorbar(x, g[sp], yerr=1.96 * g[f"{sp}_se"], fmt="o-", color=f, lw=2, ms=8, mec=FL, mew=1.5, label=name)
        for xx, v, jahr in zip(x, g[sp], g.jahr):
            # 2012 liegen die Punkte dicht beieinander: links beziehungsweise oberhalb beschriften
            versatz = ((-26, -4) if sp == "de" else (10, 4)) if jahr == 2012 else (10, dy)
            ax.annotate(f"{v:.0f}", (xx, v), xytext=versatz, textcoords="offset points", fontsize=9, color=TXT2)
    ax.set_xticks([2012, 2018, 2024])
    ax.set_xlim(2011, 2025.5)
    ax.set_ylim(455, 520)
    ax.grid(axis="x", visible=False)
    ax.set_ylabel("IQB-Berichtsskala (Achse beginnt bei 455)")
    ax.legend(frameon=False, loc="upper right")
    _fertig(fig, "7_iqb_klasse9", "Reale Aggregate: Mathematik Klasse 9, Globalskala",
            "Eigene Darstellung nach IQB-Bildungstrend 2024, Zusatztabelle 4.1web, CC BY-NC-SA 4.0, verändert. Balken: ±1,96 SE.")


def iqb_bereiche(t):
    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    y = np.arange(len(t))[::-1]
    for sp, f, off, name in (("de", BLAU, 0.13, "Deutschland"), ("mv", ORANGE, -0.13, "Mecklenburg-Vorpommern")):
        ax.errorbar(t[f"{sp}_2024"], y + off, xerr=1.96 * t[f"{sp}_se_2024"], fmt="o", ms=8, color=f, lw=2, mec=FL,
                    mew=1.5, label=name)
        for yy, v, s in zip(y + off, t[f"{sp}_2024"], t[f"{sp}_se_2024"]):
            ax.text(v + 1.96 * s + 0.6, yy, f"{v:.0f}", va="center", fontsize=9, color=TXT2)
    ax.set_yticks(y, [f"{b}{' *' if s else ''}" for b, s in zip(t.bezeichnung, t.sig_2024)])
    ax.set_xlim(440, 500)
    ax.set_ylim(-0.6, len(t) - 0.4)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("IQB-Berichtsskala 2024 (Achse beginnt bei 440), Balken: ±1,96 SE")
    ax.legend(frameon=False, loc="upper right")
    _fertig(fig, "8_iqb_bereiche", "Reale Aggregate: Klasse 9 nach Kompetenzbereich, 2024",
            "* laut IQB signifikant verschieden (p < .05). Nach IQB-Bildungstrend 2024, Tab. 4.2web bis 4.6web, CC BY-NC-SA 4.0, verändert.")


def alle(r):
    profil(r["profil"])
    baender(r["baender"])
    verteilung(r["sim"])
    veraenderung(r["veraenderung"])
    gruppen(r["gruppen"])
    sicherheit(r["sicherheit"])
    iqb(r["iqb"])
    iqb_bereiche(r["iqb_bereiche"])
