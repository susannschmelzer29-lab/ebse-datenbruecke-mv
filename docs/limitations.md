# Grenzen und Annahmen

## Was dieses Projekt nicht ist
- kein Produkt, kein Auftrag und keine Veröffentlichung des Bildungsministeriums M-V
- kein Kompetenzmonitoring für M-V, sondern ein Ausschnitt: Mathematik, Klasse 5 und 6, simuliert
- keine Bewertung realer Schulen oder Kinder

## Daten
- **Kompetenzdaten für Klasse 5 und 6 wurden öffentlich nicht gefunden.** Die Individualdaten sind vollständig simuliert.
- Die Simulation zeigt, dass die **Methode** funktioniert. Sie enthält nur Zusammenhänge, die vorher gesetzt wurden.
- Klasse 4 (2021), Klasse 5/6 (Simulation) und Klasse 9 (2024) ergeben **keinen Lernverlauf**.
- Für M-V weist der IQB-Bildungstrend 2021 keine Ergebnisse aus.
- Aus einem PDF (Q4) werden nur zwei Zeilen gelesen. Ändert sich das Layout, bricht der Import bewusst ab.

- **Nicht alle Schularten sind abgebildet.** Die Simulation enthält nur Regionale Schulen und Gesamtschulen. Förderschulen,
  Waldorfschulen und Gymnasien fehlen. Aussagen über Kinder an Förderschulen sind damit auch im Modell nicht möglich.
- Warum es in M-V Kinder in Klasse 5 und 6 am Gymnasium gibt (2025/26: 689 und 662), ist hier nicht geklärt.

## Datenqualität
- Die Simulationsfehler und die Regeln stammen vom selben Team. Vollständige Erkennung ist erwartbar und kein Beleg für
  Wirksamkeit bei unbekannten Fehlern.
- Negative Standardfehler werden verworfen, nicht durch Vorzeichenwechsel „repariert“. Die Ursache ist unbekannt.
- Die Erklärung der Differenz 15.248 gegen 14.539 ist aus Schularten und Rechnung abgeleitet, nicht aus einer Fußnote.
- „Gymnasium in Klasse 5/6“ bleibt Warnung: Die Zahlen sind in zwei amtlichen Quellen belegt, die Ausnahme ist fachlich zu klären.
- Die Befunde betreffen Tabellendateien. Sie sagen nichts über die wissenschaftliche Qualität der Studien.

## Methode
- Die drei Bänder sind **keine** amtlichen Kompetenzstufen und keine Mindeststandards.
- **20 Aufgaben je Leitidee reichen für sichere Einzeleinstufungen nicht.** Rund 26 Prozent der Bänder wären falsch, meist um
  ein Band. Bei über 80 Prozent der fiktiven Kinder schließt der Test das Nachbarband nicht aus; das ist ein strengeres Maß
  und nicht mit „falsch eingestuft“ gleichzusetzen. Bänder eignen sich hier vor allem für Gruppen.
- **40 Aufgaben lösen das nicht:** rund 19 Prozent falsche Bänder bei 200 Aufgaben je Kind. Das Gesamtergebnis aus 5 mal 20
  Aufgaben liegt bei rund 12 Prozent.
- Diese Anteile gelten für die gesetzten Simulationsparameter und für Kinder, deren Leistung am Testtag fest ist.
  Tagesform, Raten und ungleich schwere Aufgaben sind nicht getrennt modelliert.
- Intervalle: Bootstrap über Schulen. Geplant waren Klassen; Schulen sind die richtige Einheit, weil Schulart und Raumtyp auf
  Schulebene liegen. Bei 12 Schulen sind die Intervalle eher zu schmal (Trefferquote 87 bis 96 statt 95 Prozent).
- Eine von fünf Veränderungen (L5) verfehlt im Hauptlauf den gesetzten Wert knapp. Das wurde nicht nachjustiert.
- Gleiches Instrument zu zwei Zeitpunkten: Übungs- und Deckeneffekte sind nicht modelliert.
- Fehlende Messungen sind in der Simulation zufällig. In der Praxis wäre das zu prüfen.
- Gruppenunterschiede sind beschreibend, nie ursächlich.

- **Sprache und Lesen:** Mathematikergebnisse hängen auch vom Textverständnis ab. Das ist nicht modelliert.
- **Nachteilsausgleich und Förderbedarf** sind nicht abgebildet. Ein Ergebnis ohne diese Information kann ein Kind falsch
  darstellen.
- Je Leitidee erhält ein einzelnes Kind kein Band. Auch das Gesamtband darf nie allein eine Förderentscheidung begründen.

## Technik
- Getestet unter Windows 11 mit Python 3.14, andere Systeme nicht.
- Der Abruf hängt von Internetadressen der Herausgeber ab. Neue Fassungen werden erkannt und gestoppt.
- Keine Benutzerverwaltung, keine Verschlüsselung: nicht für personenbezogene Daten geeignet.

## Recht
- Schulgesetz M-V und SchulDSVO M-V wurden nicht geprüft. Das Projekt enthält keine Rechtsberatung.
- Lizenz von Q3 ist ungeklärt. Für Q2 gilt CC BY-NC-SA 4.0 (nicht kommerziell).
