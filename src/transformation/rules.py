"""Fachliche Stammdaten: Erhebungsverfahren und Vergleichsregeln."""

# (id, quelle, bezeichnung, grundgesamtheit, skala, ist_simuliert)
VERFAHREN = [
    ("V_DESTATIS_SCHUELER", "Q1", "Schulstatistik, Tabelle 21111-04",
     "alle Schularten einschließlich Förder- und Waldorfschulen", "Anzahl", 0),
    ("V_DESTATIS_WIEDERHOLER", "Q1", "Schulstatistik, Tabelle 21111-07",
     "für M-V ohne Förder- und Waldorfschulen (aus den Schularten der Tabelle abgeleitet)",
     "Anzahl und Prozent", 0),
    ("V_DESTATIS_KLASSEN", "Q1", "Schulstatistik, Tabelle 21111-02",
     "für M-V ohne Förderschulen; jahrgangsübergreifende Klassen separat", "Anzahl", 0),
    ("V_STATAMT_MV", "Q4", "Statistischer Bericht M-V, Tabelle 1.9",
     "alle Schularten, jahrgangsübergreifend Unterrichtete aufgeteilt", "Anzahl", 0),
    ("V_IQB24_KL9_ALLE", "Q2", "IQB-Bildungstrend 2024, Mittelwerte",
     "alle Neuntklässlerinnen und Neuntklässler", "IQB-Berichtsskala Sekundarstufe I", 0),
    ("V_IQB24_KL9_ZIELGLEICH", "Q2", "IQB-Bildungstrend 2024, Standards",
     "zielgleich unterrichtete Neuntklässlerinnen und Neuntklässler", "Prozent", 0),
    ("V_IQB21_KL4", "Q3", "IQB-Bildungstrend 2021",
     "Viertklässlerinnen und Viertklässler", "IQB-Berichtsskala Primarstufe bzw. Prozent", 0),
    ("V_SIM_MATHE_OS", "SIM", "Fiktives Instrument Mathematik Orientierungsstufe",
     "fiktive Kinder", "Lösungsanteil in Prozent, 20 Aufgaben je Leitidee", 1),
]

FREI = "Projektleitung, 24.11.2026: freigegeben (Gate 2)"
SPERRE = "Projektleitung, 24.11.2026: grundsätzlich gesperrt (Entscheidung 5)"

# (id, verfahren_a, verfahren_b, kennzahl, dimension, status, begruendung, entscheidung)
REGELN = [
    ("F1", "V_DESTATIS_SCHUELER", "V_STATAMT_MV", "schueler_anzahl", "quelle", "freigegeben",
     "Gleiches Schuljahr, gleiche Grundgesamtheit. Dient nur als Plausibilitätsabgleich.", FREI),
    ("F2", "V_IQB24_KL9_ALLE", "V_IQB24_KL9_ALLE", "mittelwert", "zeit", "freigegeben",
     "Das IQB weist diese Trends selbst aus. Differenzen und Standardfehler werden aus der Quelle "
     "übernommen, nicht neu berechnet.", FREI),
    ("F3", "V_IQB24_KL9_ALLE", "V_IQB24_KL9_ALLE", "mittelwert", "land", "freigegeben",
     "Vergleich mit Deutschland im selben Jahr, Test und Kompetenzbereich ist Zweck der Studie. "
     "Kein Ranking.", FREI),
    ("F4", "V_IQB24_KL9_ZIELGLEICH", "V_IQB24_KL9_ZIELGLEICH", "ms_msa_verfehlt", "land", "freigegeben",
     "Wie F3, für den Anteil unter dem Mindeststandard.", FREI),
    ("F5", "V_IQB24_KL9_ZIELGLEICH", "V_IQB24_KL9_ZIELGLEICH", "ms_msa_verfehlt", "zeit", "freigegeben",
     "Wie F2, für den Anteil unter dem Mindeststandard.", FREI),
    ("F6", "V_SIM_MATHE_OS", "V_SIM_MATHE_OS", "loesungsanteil", "zeit", "freigegeben",
     "Beide Messzeitpunkte nutzen per Konstruktion dasselbe fiktive Instrument, gepaart je Kind.", FREI),
    ("F7", "V_SIM_MATHE_OS", "V_SIM_MATHE_OS", "loesungsanteil", "gruppe", "freigegeben",
     "Alle Gruppen bearbeiten per Konstruktion dieselben Aufgaben. Beschreibend, nicht kausal, "
     "Mindestgröße 10.", FREI),
    ("S1", "V_IQB21_KL4", "V_IQB24_KL9_ALLE", "*", "quelle", "gesperrt",
     "Klasse 4 und Klasse 9: andere Kohorten, Tests und Skalen. Kein Lernverlauf ableitbar.", SPERRE),
    ("S2", "V_IQB21_KL4", "V_IQB24_KL9_ZIELGLEICH", "*", "quelle", "gesperrt", "Wie S1.", SPERRE),
    ("S3", "V_SIM_MATHE_OS", "V_IQB24_KL9_ALLE", "*", "quelle", "gesperrt",
     "Simulierte Werte dürfen nie mit realen Ergebnissen verglichen werden.", SPERRE),
    ("S4", "V_SIM_MATHE_OS", "V_IQB24_KL9_ZIELGLEICH", "*", "quelle", "gesperrt", "Wie S3.", SPERRE),
    ("S5", "V_SIM_MATHE_OS", "V_IQB21_KL4", "*", "quelle", "gesperrt", "Wie S3.", SPERRE),
    ("S6", "V_DESTATIS_SCHUELER", "V_DESTATIS_WIEDERHOLER", "schueler_anzahl", "quelle", "gesperrt",
     "Verschiedene Grundgesamtheiten: Die Wiederholertabelle enthält für M-V keine Förder- und "
     "Waldorfschulen.", SPERRE),
    ("S7", "V_IQB24_KL9_ALLE", "V_IQB24_KL9_ZIELGLEICH", "*", "quelle", "gesperrt",
     "Alle Neuntklässler gegenüber nur zielgleich Unterrichteten: verschiedene Grundgesamtheiten.", SPERRE),
]
