"""Berichte erzeugen: Datenqualität und Bildungsanalyse (Markdown), eigenständiger HTML-Bericht."""
import base64
import html

import pandas as pd

from src.config import BAENDER, DASHBOARD, QUELLEN, REPORTS
from src.reporting.charts import ORDNER
from src.transformation.simulate import PARAMETER

LEGENDE = {
    "1_kompetenzprofil": "Kompetenzprofil", "2_baender": "Verteilung auf Bänder",
    "3_verteilung": "Häufigkeitsverteilung", "4_veraenderung": "Veränderung zwischen den Messzeitpunkten",
    "5_gruppen": "Gruppenvergleiche", "6_einstufungssicherheit": "Sicherheit der Einzeleinstufung",
    "7_iqb_klasse9": "Reale Aggregate Klasse 9",
    "8_iqb_bereiche": "Reale Aggregate Klasse 9 nach Kompetenzbereich"}


def _z(v, n=1):
    if isinstance(v, bool):
        return "ja" if v else "nein"
    if isinstance(v, float):
        if v != v:  # NaN
            return ""
        return f"{v:.{n}f}".replace(".", ",")
    return "" if v is None else str(v)


def _tsd(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def md(df: pd.DataFrame, n=1) -> str:
    kopf = "| " + " | ".join(df.columns) + " |\n|" + "---|" * len(df.columns) + "\n"
    return kopf + "".join("| " + " | ".join(_z(x, n).replace("|", "/") for x in r) + " |\n"
                          for r in df.itertuples(index=False, name=None))


def tabelle(df: pd.DataFrame, n=1) -> str:
    kopf = "".join(f"<th>{html.escape(str(c))}</th>" for c in df.columns)
    zeilen = "".join("<tr>" + "".join(f"<td>{html.escape(_z(x, n))}</td>" for x in r) + "</tr>"
                     for r in df.itertuples(index=False, name=None))
    return f'<div class="tw"><table><thead><tr>{kopf}</tr></thead><tbody>{zeilen}</tbody></table></div>'


# ------------------------------------------------------------- Tabellen für beide Formate
def tab_bewertung(con, n_real, n_roh, n_sauber) -> pd.DataFrame:
    befunde = pd.read_sql("SELECT * FROM dq_befund", con)
    out = []
    for q in [*QUELLEN, "SIM"]:
        b = befunde[befunde.quelle_id == q]
        geprueft = n_roh if q == "SIM" else n_real.get(q, 0)
        je_regel = ", ".join(f"{r} ({n})" for r, n in b.regel_id.value_counts().sort_index().items())
        nutzbar = n_sauber if q == "SIM" else geprueft
        out.append({"Quelle": q, "Geprüfte Werte": geprueft, "Befunde": len(b),
                    "Vollständig nutzbar %": 100.0 * nutzbar / geprueft,
                    "Befunde je Regel (Anzahl)": je_regel or "keine"})
    return pd.DataFrame(out)


def tab_regeln(con) -> pd.DataFrame:
    return pd.read_sql(
        "SELECT r.regel_id AS Regel, r.pruefart AS Prüfart, r.beschreibung AS Beschreibung, "
        "r.schweregrad AS Schweregrad, "
        "SUM(CASE WHEN b.quelle_id <> 'SIM' THEN 1 ELSE 0 END) AS 'Befunde real', "
        "SUM(CASE WHEN b.quelle_id = 'SIM' THEN 1 ELSE 0 END) AS 'Befunde simuliert' "
        "FROM dq_regel r LEFT JOIN dq_befund b USING (regel_id) GROUP BY r.regel_id ORDER BY r.regel_id", con).fillna(0)


def tab_real(con) -> pd.DataFrame:
    """Reale Befunde; gleichartige Schreibfehler werden je Quelle und Rohwert zusammengefasst."""
    return pd.read_sql(
        "SELECT regel_id AS Regel, quelle_id AS Quelle, "
        "CASE WHEN COUNT(*) > 1 THEN MIN(fundstelle) || ' und ' || (COUNT(*) - 1) || ' weitere' "
        "ELSE MIN(fundstelle) END AS Fundstelle, rohwert AS Rohwert, meldung AS Befund, behandlung AS Behandlung "
        "FROM dq_befund WHERE quelle_id <> 'SIM' GROUP BY regel_id, quelle_id, feld, rohwert, meldung, behandlung "
        "ORDER BY regel_id, quelle_id, Fundstelle", con)


def tab_vergleich(con) -> pd.DataFrame:
    return pd.read_sql("SELECT regel_id AS Regel, verfahren_a AS 'Verfahren A', verfahren_b AS 'Verfahren B', "
                       "kennzahl AS Kennzahl, dimension AS Dimension, status AS Status, begruendung AS Begründung "
                       "FROM vergleichsregel ORDER BY regel_id", con)


def tab_profil(r):
    t = r["profil"]
    return pd.DataFrame({"Messung": t.zeitpunkt.map({"T1": "Beginn Kl. 5", "T2": "Beginn Kl. 6"}),
                         "Leitidee": t.leitidee + " " + t.bezeichnung, "n": t.n, "Mittel %": t.mittel,
                         "95-%-Intervall": [f"{_z(u)} bis {_z(o)}" for u, o in zip(t.ki_u, t.ki_o)], "SD": t.sd})


def tab_baender_gesamt(r):
    t = r["baender_gesamt"].pivot(index="band", columns="zeitpunkt_id", values="anteil")
    t = t.reindex([b for _, b in BAENDER]).reset_index()
    return pd.DataFrame({"Band (Gesamtergebnis)": t.band, "Beginn Kl. 5 %": t.T1, "Beginn Kl. 6 %": t.T2})


def tab_veraenderung(r):
    t = r["veraenderung"]
    return pd.DataFrame({"Leitidee": t.leitidee + " " + t.bezeichnung, "n gepaart": t.n_gepaart,
                         "Veränderung": t["diff"], "95-%-Intervall": [f"{_z(u)} bis {_z(o)}" for u, o in zip(t.ki_u, t.ki_o)],
                         "gesetzt": t.gesetzt, "gesetzter Wert im Intervall": [bool(x) for x in t.gesetzt_im_ki]})


def tab_gruppen(r):
    t = r["gruppen"]
    t = t[~t.unterdrueckt]
    return pd.DataFrame({"Merkmal": t.merkmal, "Vergleich": t.gruppe_a + " minus " + t.gruppe_b,
                         "Kinder": [f"{a:.0f} / {b:.0f}" for a, b in zip(t.n_a, t.n_b)],
                         "Schulen": [f"{a:.0f} / {b:.0f}" for a, b in zip(t.schulen_a, t.schulen_b)],
                         "Unterschied": t["diff"],
                         "95-%-Intervall": [f"{_z(u)} bis {_z(o)}" for u, o in zip(t.ki_u, t.ki_o)]})


def tab_iqb(r):
    t = r["iqb"]
    t = t[t.kompetenz_id == "SEK1-0"]
    kz = {"mittelwert": "Mittelwert (Skala)", "ms_msa_verfehlt": "Mindeststandard MSA verfehlt (%)"}
    return pd.DataFrame({"Kennzahl": t.kennzahl.map(kz), "Jahr": t.jahr,
                         "M-V (SE)": [f"{_z(a)} ({_z(b)})" for a, b in zip(t.mv, t.mv_se)],
                         "Deutschland (SE)": [f"{_z(a)} ({_z(b)})" for a, b in zip(t.de, t.de_se)],
                         "Regel": t.regel, "Fundstelle M-V": t.fundstelle_mv})


def tab_bereiche(r):
    t, ja = r["iqb_bereiche"], lambda s: "ja" if s else "nein"

    def lage(z, jahr):  # Richtung mitnennen: signifikant kann auch "besser" heißen
        if not z[f"sig_{jahr}"]:
            return "–"
        return "darüber" if z[f"mv_{jahr}"] > z[f"de_{jahr}"] else "darunter"

    return pd.DataFrame({"Kompetenzbereich": t.bezeichnung, "M-V 2024": [_z(x, 0) for x in t.mv_2024],
                         "Deutschland 2024": [_z(x, 0) for x in t.de_2024],
                         "Abstand": [f"{x:+.0f}" for x in t.abstand_2024],
                         "M-V zu Deutschland 2012 / 2018 / 2024 (– = nicht signifikant)": [" / ".join(lage(z, j) for j in (2012, 2018, 2024))
                                                                for _, z in t.iterrows()],
                         "Veränderung M-V 2012–2024 (SE)": [f"{a:+.0f} ({_z(b)})" for a, b in zip(t.veraenderung_mv, t.veraenderung_mv_se)],
                         "Veränderung signifikant": [ja(x) for x in t.veraenderung_mv_sig],
                         "Veränderung Deutschland": [f"{x:+.0f}" for x in t.veraenderung_de],
                         "MSA-Mindeststandard verfehlt M-V / D %": [f"{_z(a)} / {_z(b)}" for a, b in zip(t.ms_mv_2024, t.ms_de_2024)]})


TEXT_BEREICHE = ("2024 liegt M-V nur in „Messen“ laut IQB signifikant unter Deutschland, dort auch schon 2012 und 2018. Der Wert sank dort in beiden Räumen seit 2012 um 32 Punkte, der Rückstand blieb also etwa gleich. In allen fünf Bereichen sind die Werte in M-V seit 2012 laut IQB signifikant gesunken. Ursachen lassen sich daraus nicht ableiten. Ob das IQB für mehrere Vergleiche korrigiert, wurde nicht geprüft. Für „Größen und Messen“ in Klasse 5/6 folgt daraus kein Befund, sondern eine Frage: Zeigt sich eine Schwäche schon in der Lernausgangslage?")


def tab_trend(r):
    t = r["iqb_trend"]
    return pd.DataFrame({"Raum": t.land_id.map({"MV": "M-V", "DE": "Deutschland"}), "Zeitraum": t.zeitpunkt_id,
                         "Veränderung (vom IQB berichtet)": t.differenz, "SE (vom IQB berichtet)": t.se})


def tab_abgleich(abgleich):
    return pd.DataFrame({"Klasse": abgleich.klassenstufe, "Schulart": abgleich.art,
                         "Destatis": abgleich.V_DESTATIS_SCHUELER, "Stat. Amt M-V": abgleich.V_STATAMT_MV,
                         "stimmt überein": [bool(x) for x in abgleich.stimmt]})


def tab_testlaenge(datei="SIM_testlaenge_je_leitidee.csv"):
    """Ergebnis von src.analytics.testlaenge (eigenes Experiment)."""
    t = pd.read_csv(REPORTS / datei)
    return pd.DataFrame({"Aufgaben je Leitidee": t.get("aufgaben_je_leitidee", t.aufgaben),
                         "Bereich berührt Bandgrenze %": t.unsicher_prozent,
                         "falsches Band %": t.falsch_prozent,
                         "um zwei Bänder falsch %": t.zwei_baender_falsch_prozent,
                         "halbe Intervallbreite": t.halbe_intervallbreite})


# ------------------------------------------------------------- Berichte
HINWEIS_SIM = ("**SIMULIERTE DATEN.** Alle Kinder und Schulen sind erfunden. Die Ergebnisse zeigen analytische "
               "Möglichkeiten und sagen nichts über tatsächliche Kinder, Schulen oder das Land aus.")


def dq_bericht(con, r, leistung, abgleich, bewertung, n_roh, n_sauber) -> str:
    n_stellen = int(leistung.eingebaut.sum())
    return f"""# Datenqualitätsbericht

Automatisch erzeugt durch `python -m src.run_all`. Rohdaten wurden nicht verändert.

## 1. Ergebnis je Quelle

{md(bewertung)}
„Vollständig nutzbar“ heißt: in die Datenbank übernommen. Bei realen Quellen bleibt der Wert auch dann erhalten,
wenn nur sein Standardfehler verworfen wurde. Befunde können mehrere Werte zusammenfassen.

## 2. Qualitätsregeln

{md(tab_regeln(con))}
## 3. Befunde in den realen Quellen

{md(tab_real(con))}
## 4. Abgleich zweier amtlicher Quellen (Regel DQ10)

Schülerzahlen in Mecklenburg-Vorpommern, Schuljahr 2025/26. {int(abgleich.stimmt.sum())} von {len(abgleich)} Werten
stimmen überein.

{md(tab_abgleich(abgleich))}
## 5. Simulierte Daten: Werden eingebaute Fehler erkannt?

In {n_roh} Rohzeilen wurden {n_stellen} Fehlerstellen eingebaut. {n_sauber} Zeilen sind auswertbar,
{n_roh - n_sauber} bleiben ausgeschlossen, aber in der Rohdatei erhalten.

{md(leistung.rename(columns=dict(regel_id="Regel", uebersehen="übersehen")))}
**Einordnung:** Fehler und Regeln stammen vom selben Team. Eine vollständige Erkennung belegt, dass die Regeln wie
beschrieben arbeiten. Sie belegt nicht, dass unbekannte Fehler in echten Daten gefunden würden.

## 6. Vergleichbarkeit

{md(tab_vergleich(con))}
Bewusst versuchte unzulässige Vergleiche:

{"".join(f"- **{a}:** {b}" + chr(10) for a, b in r["sperren"])}"""


def analyse_bericht(r) -> str:
    v, s = r["veraenderung"], r["sicherheit"]
    s2 = s[s.zeitpunkt_id == "T2"].anteil
    return f"""# Exemplarische Bildungsanalyse Mathematik, Klassenstufe 5 und 6

{HINWEIS_SIM}

Automatisch erzeugt durch `python -m src.run_all`. Startwert der Simulation: {PARAMETER["seed"]}.

## Was gemessen wird

Lösungsanteil in einem fiktiven Test mit 20 Aufgaben je Leitidee (L1 bis L5 nach Rahmenplan Mathematik M-V 2026).
Die drei Bänder (unter 50, 50 bis unter 75, ab 75 Prozent) hat die Projektleitung festgelegt. Sie sind **keine**
amtlichen Kompetenzstufen und keine Mindeststandards.

## 1. Kompetenzprofil

![Kompetenzprofil](grafiken/1_kompetenzprofil.png)

{md(tab_profil(r))}
## 2. Bänder und Verteilung

![Bänder](grafiken/2_baender.png)

![Verteilung](grafiken/3_verteilung.png)

{md(tab_baender_gesamt(r))}
Bänder je Leitidee werden nur für Gruppen ausgewiesen. Für ein einzelnes Kind gibt es ausschließlich ein Band über das
Gesamtergebnis, nie als alleinige Grundlage für Förderung (Entscheidung PL-19).

## 3. Veränderung zwischen zwei Messzeitpunkten

![Veränderung](grafiken/4_veraenderung.png)

{md(tab_veraenderung(r))}
Bei {int(v.gesetzt_im_ki.sum())} von {len(v)} Leitideen enthält das Intervall den gesetzten Wert. In 100 wiederholten
Simulationen lag die Trefferquote je Leitidee zwischen 87 und 96 Prozent (`SIM_ueberdeckung.csv`). Die Intervalle sind
bei nur 12 Schulen also teils etwas zu schmal.

## 4. Gruppenvergleiche

![Gruppen](grafiken/5_gruppen.png)

{md(tab_gruppen(r))}
Für die Schulart wurde ein kleiner Unterschied eingebaut, für den Raumtyp keiner. Beide Intervalle schließen null ein:
Bei 4 gegen 8 Schulen ist ein kleiner Unterschied nicht sicher nachweisbar. Das ist ein Ergebnis über die nötige
Stichprobengröße, kein Beleg für „kein Unterschied“.

## 5. Sicherheit der Einzeleinstufung

![Einstufungssicherheit](grafiken/6_einstufungssicherheit.png)

Bei {_z(float(s2.min()), 0)} bis {_z(float(s2.max()), 0)} Prozent der fiktiven Kinder reicht der 95-%-Bereich ihres
Ergebnisses über eine Bandgrenze (Beginn Klasse 6). Das heißt nicht, dass ihre Einstufung falsch ist, sondern dass
der Test das benachbarte Band nicht ausschließt. Wie oft die Einstufung tatsächlich falsch ist, zeigt der folgende
Vergleich, denn in der Simulation ist der wahre Lösungsanteil bekannt (40.000 fiktive Kinder je Testlänge).

**Einstufung je Leitidee**

{md(tab_testlaenge())}
**Einstufung über alle fünf Leitideen zusammen**

{md(tab_testlaenge("SIM_testlaenge_gesamt.csv"))}
Mehr Aufgaben helfen, aber langsam: Von 20 auf 40 Aufgaben je Leitidee sinkt der Anteil falscher Bänder nur um rund
ein Viertel, der Test verdoppelt sich auf 200 Aufgaben. Das Gesamtergebnis aus 5 mal 20 Aufgaben ist
treffsicherer als jede einzelne Leitidee mit 40 Aufgaben. Für Gruppenmittel wurde die Testlänge nicht untersucht. Ein Band allein darf
keine Förderentscheidung begründen.

## 6. Reale Aggregate: Klasse 9, getrennt von der Simulation

![IQB](grafiken/7_iqb_klasse9.png)

{md(tab_iqb(r))}
{md(tab_trend(r))}
### Nach Kompetenzbereich

![Kompetenzbereiche](grafiken/8_iqb_bereiche.png)

{md(tab_bereiche(r))}
{TEXT_BEREICHE} Abstände sind aus ungerundeten Werten berechnet, soweit die Quelle sie enthält.

Quelle: IQB-Bildungstrend 2024, Zusatzmaterial Tabellen, Stand 25.06.2026, CC BY-NC-SA 4.0, eigene Auswahl und
Darstellung. Veränderungen und ihre Standardfehler sind übernommen, weil sie nicht allein aus den Einzelwerten
berechenbar sind. Die Werte betreffen Klasse 9 und sind mit Klasse 5/6 nicht vergleichbar.
"""


CSS = """:root{--bg:#f4f5f7;--fl:#fcfcfb;--tx:#14181f;--tx2:#52514e;--li:#dcdfe4;--ak:#1c5cab;--sim:#8a3b12;--simbg:#fdeee5}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--tx);font:16px/1.55 "Segoe UI",system-ui,sans-serif}
main{max-width:1040px;margin:0 auto;padding:32px 20px 64px}h1{font-size:30px;line-height:1.2;margin:0 0 8px}
h2{font-size:21px;margin:44px 0 12px;padding-top:16px;border-top:1px solid var(--li)}p{max-width:72ch}
.sim{background:var(--simbg);border-left:4px solid var(--sim);padding:10px 14px;max-width:none}
.real{background:#e8f0fa;border-left:4px solid var(--ak);padding:10px 14px;max-width:none}
img{width:100%;height:auto;display:block;background:var(--fl);border:1px solid var(--li);margin:14px 0}
.kz{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:20px 0}
.kz div{background:var(--fl);border:1px solid var(--li);padding:14px}.kz b{display:block;font-size:26px}
.kz span{color:var(--tx2);font-size:14px}.tw{overflow-x:auto;margin:12px 0}
table{border-collapse:collapse;width:100%;font-size:14px;background:var(--fl)}
th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--li);vertical-align:top}th{background:#eceef1}
td{font-variant-numeric:tabular-nums}nav a{margin-right:16px}a{color:var(--ak)}
summary{cursor:pointer;color:var(--ak);padding:6px 0}@media print{body{background:#fff}}"""


def html_bericht(con, r, leistung, abgleich, bewertung, n_real, n_roh, n_sauber) -> str:
    def bild(name):
        b = base64.b64encode((ORDNER / f"{name}.png").read_bytes()).decode()
        return f'<img alt="{html.escape(LEGENDE[name])}" src="data:image/png;base64,{b}">'

    def klapp(titel, inhalt):
        return f"<details><summary>{html.escape(titel)}</summary>{inhalt}</details>"

    s2 = r["sicherheit"][r["sicherheit"].zeitpunkt_id == "T2"].anteil
    sim = '<p class="sim"><strong>Simulierte Daten.</strong> Alle Kinder und Schulen sind erfunden. Keine Aussage über reale Verhältnisse.</p>'
    real = '<p class="real"><strong>Reale, aggregierte Daten.</strong> Amtliche Statistik und IQB, jede Zahl bis zur Originalzelle nachverfolgbar.</p>'
    sperren = "".join(f"<li><strong>{html.escape(a)}:</strong> {html.escape(b)}</li>" for a, b in r["sperren"])
    return f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>EBSE-Datenbrücke M-V</title><style>{CSS}</style></head><body><main>
<h1>EBSE-Datenbrücke M-V</h1>
<p>Demonstrator für Datenmanagement und Kompetenzmonitoring in Mathematik, Klassenstufe 5 und 6. Eigenständiger Prototyp,
keine Lösung oder Veröffentlichung des Bildungsministeriums.</p>
<nav><a href="#dq">Datenqualität</a><a href="#vgl">Vergleichbarkeit</a><a href="#real">Reale Aggregate</a><a href="#sim">Simulation</a></nav>
<div class="kz"><div><b>{_tsd(sum(n_real.values()))}</b><span>reale Werte mit Fundstelle</span></div>
<div><b>{int(abgleich.stimmt.sum())} von {len(abgleich)}</b><span>Werten stimmen zwischen zwei Ämtern überein</span></div>
<div><b>{_tsd(n_sauber)} von {_tsd(n_roh)}</b><span>simulierten Zeilen auswertbar</span></div>
<div><b>{len(r["sperren"])} von {len(r["sperren"])}</b><span>unzulässigen Testvergleichen abgewiesen</span></div></div>
<h2 id="dq">1. Datenqualität</h2>{real}{tabelle(bewertung)}
<h3>Befunde in den realen Quellen</h3>{tabelle(tab_real(con))}
{klapp("Abgleich Destatis und Statistisches Amt M-V", tabelle(tab_abgleich(abgleich)))}
{klapp("Alle Qualitätsregeln", tabelle(tab_regeln(con)))}
{klapp("Erkennung eingebauter Fehler in der Simulation", tabelle(leistung))}
<p>Fehler und Regeln der Simulation stammen vom selben Team. Vollständige Erkennung belegt, dass die Regeln wie beschrieben
arbeiten, nicht, dass unbekannte Fehler gefunden würden.</p>
<h2 id="vgl">2. Vergleichbarkeit</h2><p>Ohne begründete Freigabe gilt jeder Vergleich als unzulässig. Diese Versuche hat das System abgewiesen:</p>
<ul>{sperren}</ul>{klapp("Alle Vergleichsregeln", tabelle(tab_vergleich(con)))}
<h2 id="real">3. Reale Aggregate: Mathematik Klasse 9</h2>{real}{bild("7_iqb_klasse9")}
{klapp("Werte und Fundstellen", tabelle(tab_iqb(r)) + tabelle(tab_trend(r)))}
<h3>Nach Kompetenzbereich</h3>{bild("8_iqb_bereiche")}<p>{TEXT_BEREICHE}</p>
{klapp("Werte je Kompetenzbereich", tabelle(tab_bereiche(r)))}
<p>Quelle: IQB-Bildungstrend 2024, Zusatzmaterial Tabellen, CC BY-NC-SA 4.0, eigene Auswahl und Darstellung. Für Klasse 4 (2021)
weist das IQB für Mecklenburg-Vorpommern keine Ergebnisse aus. Ein Verlauf von Klasse 4 bis 9 ist nicht ableitbar.</p>
<h2 id="sim">4. Exemplarisches Kompetenzmonitoring</h2>{sim}
{bild("1_kompetenzprofil")}{klapp("Werte", tabelle(tab_profil(r)))}
{bild("2_baender")}{bild("3_verteilung")}{klapp("Bänder über das Gesamtergebnis", tabelle(tab_baender_gesamt(r)))}
<p>Bänder je Leitidee gelten nur für Gruppen. Für einzelne Kinder gibt es nur ein Band über das Gesamtergebnis, nie als alleinige Grundlage für Förderung.</p>
{bild("4_veraenderung")}{klapp("Werte", tabelle(tab_veraenderung(r)))}
{bild("5_gruppen")}{klapp("Werte", tabelle(tab_gruppen(r)))}
{bild("6_einstufungssicherheit")}
<p>Bei {_z(float(s2.min()), 0)} bis {_z(float(s2.max()), 0)} Prozent der fiktiven Kinder reicht die Messunsicherheit über eine
Bandgrenze. Das heißt nicht, dass die Einstufung falsch ist, sondern dass der Test das Nachbarband nicht ausschließt.
Tatsächlich falsch wäre das Band je Leitidee in rund {_z(float(tab_testlaenge().set_index("Aufgaben je Leitidee").loc[20, "falsches Band %"]), 0)} Prozent der Fälle.</p>
<h3>Wie viel bringen mehr Aufgaben?</h3><p>Einstufung je Leitidee:</p>{tabelle(tab_testlaenge())}
<p>Einstufung über alle fünf Leitideen zusammen:</p>{tabelle(tab_testlaenge("SIM_testlaenge_gesamt.csv"))}{sim}
</main></body></html>
"""


def schreibe(con, r, leistung, abgleich, n_real, n_roh, n_sauber) -> None:
    REPORTS.mkdir(exist_ok=True)
    DASHBOARD.mkdir(exist_ok=True)
    bew = tab_bewertung(con, n_real, n_roh, n_sauber)
    opt = dict(encoding="utf-8", newline="\n")
    (REPORTS / "datenqualitaetsbericht.md").write_text(dq_bericht(con, r, leistung, abgleich, bew, n_roh, n_sauber), **opt)
    (REPORTS / "bildungsanalyse.md").write_text(analyse_bericht(r), **opt)
    (DASHBOARD / "index.html").write_text(html_bericht(con, r, leistung, abgleich, bew, n_real, n_roh, n_sauber), **opt)
