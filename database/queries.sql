-- Beispielabfragen zur EBSE-Datenbrücke (SQLite, Datei data/processed/ebse.sqlite)
-- Reale Aggregate und simulierte Daten werden nie in einer Abfrage verbunden.

-- 1. Data Lineage: Woher stammt der Mittelwert für M-V 2024?
SELECT land, kompetenz, zeitpunkt_id, wert, se, land_roh, datei, blatt, zelle, abgerufen_utc
FROM v_lineage
WHERE land = 'Mecklenburg-Vorpommern' AND kennzahl = 'mittelwert' AND zeitpunkt_id = '2024';

-- 2. Schüler in Klasse 5 und 6 in M-V nach Schulart, zwei Quellen nebeneinander (Regel F1)
SELECT f.klassenstufe, s.harmonisiert_mv AS schulart,
       MAX(CASE WHEN f.verfahren_id = 'V_DESTATIS_SCHUELER' THEN f.wert END) AS destatis,
       MAX(CASE WHEN f.verfahren_id = 'V_STATAMT_MV' THEN f.wert END) AS statamt_mv
FROM fact_aggregat f JOIN dim_schulform s USING (schulform_id)
WHERE f.land_id = 'MV' AND f.kennzahl = 'schueler_anzahl'
  AND f.verfahren_id IN ('V_DESTATIS_SCHUELER', 'V_STATAMT_MV')
GROUP BY f.klassenstufe, s.harmonisiert_mv
ORDER BY f.klassenstufe, schulart;

-- 3. Nicht ausgewiesene Werte mit Grund
SELECT land, klassenstufe, zeitpunkt_id, kennzahl, kompetenz, statusgrund
FROM v_lineage WHERE status = 'nicht_ausgewiesen';

-- 4. Befunde je Regel und Quelle
SELECT r.regel_id, r.pruefart, r.schweregrad, b.quelle_id, COUNT(*) AS befunde
FROM dq_befund b JOIN dq_regel r USING (regel_id)
GROUP BY r.regel_id, b.quelle_id
ORDER BY r.regel_id, b.quelle_id;

-- 5. Welche Vergleiche sind erlaubt, welche gesperrt, und wer hat entschieden?
SELECT regel_id, verfahren_a, verfahren_b, kennzahl, dimension, status, begruendung, entscheidung
FROM vergleichsregel ORDER BY status, regel_id;

-- 6. SIMULIERT: mittlerer Lösungsanteil je Leitidee und Messzeitpunkt
SELECT zeitpunkt_id, leitidee, COUNT(*) AS n, ROUND(AVG(prozent), 1) AS mittel
FROM v_simulation GROUP BY zeitpunkt_id, leitidee ORDER BY zeitpunkt_id, leitidee;

-- 7. SIMULIERT: Veränderung je Kind mit beiden Messungen (Regel F6)
SELECT a.leitidee, COUNT(*) AS n_gepaart, ROUND(AVG(b.prozent - a.prozent), 1) AS veraenderung
FROM v_simulation a
JOIN v_simulation b ON b.kind_id = a.kind_id AND b.kompetenz_id = a.kompetenz_id AND b.zeitpunkt_id = 'T2'
WHERE a.zeitpunkt_id = 'T1'
GROUP BY a.leitidee;
