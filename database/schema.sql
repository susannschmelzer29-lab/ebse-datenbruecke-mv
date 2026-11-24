-- EBSE-Datenbrücke M-V: relationales Schema (SQLite)
-- Grundsatz: reale Aggregate und simulierte Individualdaten liegen in getrennten Faktentabellen.
PRAGMA foreign_keys = ON;

CREATE TABLE dim_datenquelle (
    quelle_id     TEXT PRIMARY KEY,
    titel         TEXT NOT NULL,
    herausgeber   TEXT NOT NULL,
    bezugsjahr    TEXT NOT NULL,
    raum          TEXT NOT NULL,
    datenart      TEXT NOT NULL,
    lizenz        TEXT,
    url           TEXT,
    datei         TEXT,
    sha256        TEXT,
    abgerufen_utc TEXT,
    ist_simuliert INTEGER NOT NULL CHECK (ist_simuliert IN (0, 1))
);

-- Erhebungsverfahren: legt fest, was eine Zahl bedeutet (Grundgesamtheit, Skala, Instrument)
CREATE TABLE dim_verfahren (
    verfahren_id    TEXT PRIMARY KEY,
    quelle_id       TEXT NOT NULL REFERENCES dim_datenquelle,
    bezeichnung     TEXT NOT NULL,
    grundgesamtheit TEXT NOT NULL,
    skala           TEXT NOT NULL,
    ist_simuliert   INTEGER NOT NULL CHECK (ist_simuliert IN (0, 1))
);

CREATE TABLE dim_land (
    land_id TEXT PRIMARY KEY,
    name    TEXT NOT NULL UNIQUE
);

-- Schulform je Quelle; harmonisiert_mv gilt nur für Mecklenburg-Vorpommern
CREATE TABLE dim_schulform (
    schulform_id    INTEGER PRIMARY KEY,
    quelle_id       TEXT NOT NULL REFERENCES dim_datenquelle,
    bezeichnung     TEXT NOT NULL,
    harmonisiert_mv TEXT,
    UNIQUE (quelle_id, bezeichnung)
);

-- Kompetenzbereiche werden je Rahmen geführt, nicht über ähnliche Namen zusammengelegt
CREATE TABLE dim_kompetenz (
    kompetenz_id TEXT PRIMARY KEY,
    rahmen       TEXT NOT NULL,
    bezeichnung  TEXT NOT NULL,
    UNIQUE (rahmen, bezeichnung)
);

CREATE TABLE dim_zeitpunkt (
    zeitpunkt_id TEXT PRIMARY KEY,
    art          TEXT NOT NULL CHECK (art IN ('Schuljahr', 'Erhebungsjahr', 'Differenz', 'Messzeitpunkt')),
    beschreibung TEXT NOT NULL
);

CREATE TABLE fact_aggregat (
    fakt_id      INTEGER PRIMARY KEY,
    quelle_id    TEXT NOT NULL REFERENCES dim_datenquelle,
    verfahren_id TEXT NOT NULL REFERENCES dim_verfahren,
    land_id      TEXT NOT NULL REFERENCES dim_land,
    klassenstufe INTEGER NOT NULL CHECK (klassenstufe BETWEEN 1 AND 13),
    schulform_id INTEGER REFERENCES dim_schulform,
    kompetenz_id TEXT REFERENCES dim_kompetenz,
    zeitpunkt_id TEXT NOT NULL REFERENCES dim_zeitpunkt,
    kennzahl     TEXT NOT NULL,
    wert         REAL,
    se           REAL CHECK (se IS NULL OR se >= 0),
    status       TEXT NOT NULL CHECK (status IN ('gueltig', 'se_verworfen', 'nicht_ausgewiesen')),
    statusgrund  TEXT,
    wert_roh     TEXT,
    se_roh       TEXT,
    land_roh     TEXT,
    blatt        TEXT NOT NULL,
    zelle        TEXT NOT NULL,
    sig_de       INTEGER CHECK (sig_de IN (0, 1)),    -- laut Quelle signifikant verschieden von Deutschland
    sig_zeit     INTEGER CHECK (sig_zeit IN (0, 1)),  -- laut Quelle signifikante Veränderung
    CHECK ((status = 'nicht_ausgewiesen') = (wert IS NULL))
);
CREATE UNIQUE INDEX ux_aggregat ON fact_aggregat (
    verfahren_id, land_id, klassenstufe, IFNULL(schulform_id, -1), IFNULL(kompetenz_id, ''), zeitpunkt_id, kennzahl);

-- ----- Simulierte Individualdaten (vollständig künstlich) -----
CREATE TABLE sim_schule (
    schule_id TEXT PRIMARY KEY CHECK (schule_id LIKE 'SIM-S%'),
    name      TEXT NOT NULL CHECK (name LIKE 'Fiktive Schule%'),
    schulart  TEXT NOT NULL,
    raumtyp   TEXT NOT NULL
);

CREATE TABLE sim_kind (
    kind_id   TEXT PRIMARY KEY CHECK (kind_id LIKE 'SIM-K%'),
    schule_id TEXT NOT NULL REFERENCES sim_schule,
    klasse_id TEXT NOT NULL
);

CREATE TABLE fact_simulation (
    sim_id        INTEGER PRIMARY KEY,
    verfahren_id  TEXT NOT NULL REFERENCES dim_verfahren,
    kind_id       TEXT NOT NULL REFERENCES sim_kind,
    zeitpunkt_id  TEXT NOT NULL REFERENCES dim_zeitpunkt,
    klassenstufe  INTEGER NOT NULL CHECK (klassenstufe IN (5, 6)),
    kompetenz_id  TEXT NOT NULL REFERENCES dim_kompetenz,
    testdatum     TEXT NOT NULL,
    punkte        INTEGER NOT NULL,
    max_punkte    INTEGER NOT NULL CHECK (max_punkte > 0),
    roh_zeile     INTEGER NOT NULL,
    ist_simuliert INTEGER NOT NULL DEFAULT 1 CHECK (ist_simuliert = 1),
    CHECK (punkte BETWEEN 0 AND max_punkte),
    UNIQUE (kind_id, zeitpunkt_id, kompetenz_id)
);

-- ----- Datenqualität -----
CREATE TABLE dq_regel (
    regel_id     TEXT PRIMARY KEY,
    pruefart     TEXT NOT NULL,
    beschreibung TEXT NOT NULL,
    schweregrad  TEXT NOT NULL CHECK (schweregrad IN ('Fehler', 'Warnung', 'Hinweis'))
);

CREATE TABLE dq_befund (
    befund_id  INTEGER PRIMARY KEY,
    regel_id   TEXT NOT NULL REFERENCES dq_regel,
    quelle_id  TEXT NOT NULL REFERENCES dim_datenquelle,
    fundstelle TEXT NOT NULL,
    feld       TEXT NOT NULL,
    rohwert    TEXT,
    meldung    TEXT NOT NULL,
    behandlung TEXT NOT NULL
);

-- ----- Vergleichbarkeit: was hier nicht freigegeben ist, gilt als nicht vergleichbar -----
CREATE TABLE vergleichsregel (
    regel_id     TEXT PRIMARY KEY,
    verfahren_a  TEXT NOT NULL REFERENCES dim_verfahren,
    verfahren_b  TEXT NOT NULL REFERENCES dim_verfahren,
    kennzahl     TEXT NOT NULL,
    dimension    TEXT NOT NULL CHECK (dimension IN ('zeit', 'land', 'quelle', 'gruppe')),
    status       TEXT NOT NULL CHECK (status IN ('vorgeschlagen', 'freigegeben', 'gesperrt')),
    begruendung  TEXT NOT NULL,
    entscheidung TEXT NOT NULL
);

-- Data Lineage: jeder reale Wert bis zur Zelle der Originaldatei
CREATE VIEW v_lineage AS
SELECT f.fakt_id, l.name AS land, f.klassenstufe, f.zeitpunkt_id, f.kennzahl,
       k.bezeichnung AS kompetenz, f.wert, f.se, f.status, f.statusgrund,
       f.wert_roh, f.se_roh, f.land_roh, q.titel, q.datei, f.blatt, f.zelle,
       q.sha256, q.abgerufen_utc, q.url
FROM fact_aggregat f
JOIN dim_datenquelle q USING (quelle_id)
JOIN dim_land l USING (land_id)
LEFT JOIN dim_kompetenz k USING (kompetenz_id);

-- Auswertungssicht der Simulation
CREATE VIEW v_simulation AS
SELECT s.sim_id, s.kind_id, k.klasse_id, k.schule_id, u.schulart, u.raumtyp, s.zeitpunkt_id,
       s.klassenstufe, s.kompetenz_id, d.bezeichnung AS leitidee, s.punkte, s.max_punkte,
       100.0 * s.punkte / s.max_punkte AS prozent, s.ist_simuliert
FROM fact_simulation s
JOIN sim_kind k USING (kind_id)
JOIN sim_schule u USING (schule_id)
JOIN dim_kompetenz d USING (kompetenz_id);

-- Einzelnes Kind: Band nur für das Gesamtergebnis und nur bei vollständigem Profil (Entscheidung PL-19).
-- Je Leitidee wird bewusst kein Band für einzelne Kinder gespeichert.
CREATE VIEW v_sim_kind_gesamt AS
SELECT kind_id, klasse_id, schule_id, schulart, raumtyp, zeitpunkt_id, klassenstufe,
       SUM(punkte) AS punkte, SUM(max_punkte) AS max_punkte,
       100.0 * SUM(punkte) / SUM(max_punkte) AS prozent,
       CASE WHEN 100.0 * SUM(punkte) / SUM(max_punkte) >= 75 THEN 'sicher'
            WHEN 100.0 * SUM(punkte) / SUM(max_punkte) >= 50 THEN 'im Aufbau'
            ELSE 'Unterstützung prüfen' END AS band,
       1 AS ist_simuliert
FROM v_simulation
GROUP BY kind_id, klasse_id, schule_id, schulart, raumtyp, zeitpunkt_id, klassenstufe
HAVING COUNT(DISTINCT kompetenz_id) = 5;
