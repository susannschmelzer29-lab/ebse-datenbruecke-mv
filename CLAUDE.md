# Arbeitsregeln für KI-Assistenten in diesem Projekt

- Sprache: Deutsch. Fachliche Entscheidungen trifft die Projektleitung, siehe `DECISION_LOG.md`.
- Rohdaten in `data/raw` nie ändern, nie committen. Manifest nur nach Rücksprache anpassen.
- Reale Aggregate und simulierte Daten nie verbinden. Simuliertes immer kennzeichnen (`SIM_`, `ist_simuliert`, Grafikvermerk).
- Keine echten personenbezogenen Daten. Keine Aussagen über reale Schulen oder Kinder. Keine Kausalaussagen.
- Neue Vergleiche nur über `vergleichsregel`. Neue Regeln beginnen als `vorgeschlagen`, Freigabe durch die Projektleitung.
- Fehlerhafte Daten markieren und protokollieren, nicht stillschweigend entfernen oder korrigieren.
- Keine Quellen, Schnittstellen oder Systemeigenschaften erfinden. Unbelegtes als offene Frage führen.
- Keine Pushes, Veröffentlichungen, kostenpflichtigen Dienste oder neuen Abhängigkeiten ohne Zustimmung.
- Nach Änderungen: `python -m src.run_all` und `python -m pytest`.
