# Technische Machbarkeitsanalyse

Frage: Wie könnten Bildungsdatenquellen in M-V technisch zusammenarbeiten, ohne bestehende Systeme zu ersetzen?

**Grundlage:** öffentlich zugängliche Informationen, Stand 24.11.2026, und die Erfahrungen aus diesem Demonstrator. Über
die interne Architektur von Landessystemen wird nichts unterstellt. Was nicht öffentlich belegt ist, steht in Abschnitt 5.

## 1. Was öffentlich bekannt ist

| System | Belegt | Quelle |
|---|---|---|
| ISY-MV | Plattform für Unterrichtsorganisation und Schulverwaltung, u. a. mit Identitätenmanagement und Auswertungssystem; soll SIP künftig ablösen; genannte Anbindungen VIDIS und SDM | [bildung-mv.de](https://www.bildung-mv.de/unterricht/digitalisierung/isy-mv-und-itslearning/) |
| LEO.MV | freiwillig, Klasse 5 und 7, u. a. Mathematik; automatische Auswertung; Rückmeldung auf Aufgaben-, Gruppen- und Schülerebene | [bildung-mv.de](https://www.bildung-mv.de/schule/schulentwicklung/daten-und-evaluation/lernstandserhebungen-und-vergleichsarbeiten/) |
| VERA 3 und 8 | verpflichtend an öffentlichen Schulen, Aufgaben unter Federführung des IQB, Vergleich mit Landesergebnissen | ebenda |
| Lernlinie | Diagnostik und Förderung u. a. in Mathematik; nach eigener Angabe Landeslizenz M-V | [lernlinie.de](https://home.lernlinie.de/) |
| IQB-Bildungstrends | Stichprobe, Ergebnisse auf Landesebene; nächster Primarbereich 2027 | [KMK](https://www.kmk.org/bildungsministerkonferenz/vertiefende-bildungsinhalte/bildungsmonitoring/ueberpruefung-und-umsetzung-von-bildungsstandards.html) |
| Schulentwicklungsplanung | Aufgabe der Landkreise und kreisfreien Städte, Genehmigung durch das Ministerium, Laufzeit fünf Jahre | [land-mv.de](https://land-mv.de/thema/programme-und-schulentwicklung) |

## 2. Drei Lösungsansätze

**A. Datei- und schnittstellenbasierter Austausch.** Quellen liefern vereinbarte Dateien. Eine Prüfstrecke kontrolliert sie
gegen einen Datenvertrag und weist Abweichungen zurück. Genau das setzt dieser Demonstrator um.

**B. Zentrale relationale Datenbank.** Alle Daten werden in ein gemeinsames Schema überführt und dort gehalten.

**C. Modulare Datenplattform.** Fachsysteme bleiben eigenständig. Getrennte Bausteine für Aufnahme, Qualität, Katalog,
Vergleichbarkeit und Auswertung arbeiten über standardisierte, versionierte Schnittstellen zusammen.

| Kriterium | A Dateien | B Zentrale Datenbank | C Modulare Plattform |
|---|---|---|---|
| Technische Voraussetzungen | gering: Ablage, Prüfskripte | Datenbankbetrieb, Ladeprozesse | Schnittstellen, Katalog, Identitäten, Betrieb |
| Integration | jede Quelle einzeln, viel Handarbeit | gut, wenn sich alle auf ein Schema einigen | gut, Quellen behalten eigene Modelle |
| Skalierbarkeit | begrenzt | mittel | hoch |
| Datenschutz und Sicherheit | Kopien schwer zu kontrollieren, dafür wenig Daten | zentrale Rechte, aber hohes Risiko durch Zusammenführung | Daten bleiben beim Verantwortlichen, Zweckbindung je Baustein |
| Wartbarkeit | sinkt mit jeder Quelle | zentral, Schemaänderungen wirken überall | Bausteine einzeln änderbar |
| Erweiterbarkeit | neue Quelle = neuer Vertrag | neue Quelle = Schemaänderung | neue Quelle = neuer Baustein |
| Kostenfaktoren | Personalzeit | Betrieb, Migration | Aufbau, Betrieb, Standardisierung |
| Abhängigkeiten | Dateiformate der Lieferanten | Datenbankbetreiber | Schnittstellenstandards, mehrere Betreiber |
| Organisation | Absprachen je Lieferung | zentrale Zuständigkeit | Rollen, Datenverantwortung, Steuerung |

## 3. Entscheidungsmatrix

Skala 1 (ungünstig) bis 5 (günstig). **Punkte und Gewichte sind eine begründete Einschätzung, keine Messung.**
Vorgeschlagen vom KI-Assistenten, bestätigt durch die Projektleitung am 24.11.2026. Für einen realen Einsatz müssten IT und
Fachreferate sie überprüfen.

| Kriterium | Gewicht % | A | B | C | Begründung der Spitzen- und Tiefwerte |
|---|---|---|---|---|---|
| Technische Voraussetzungen | 10 | 5 | 3 | 2 | A läuft mit vorhandenen Mitteln, C braucht Aufbau |
| Integrationsmöglichkeiten | 15 | 2 | 3 | 5 | C erhält unterschiedliche Skalen und Modelle |
| Skalierbarkeit | 10 | 2 | 3 | 5 | Aufwand von A wächst mit jeder Datei |
| Datenschutz und Sicherheit | 20 | 3 | 3 | 4 | A und B haben gegenläufige Schwächen, C trennt Zwecke |
| Wartbarkeit | 10 | 2 | 4 | 4 | viele Einzelskripte in A |
| Erweiterbarkeit | 10 | 2 | 3 | 5 | siehe Integration |
| Kostenfaktoren | 10 | 5 | 3 | 2 | C mit höchstem Anfangsaufwand |
| Abhängigkeiten | 5 | 4 | 3 | 3 | A kaum von Plattformen abhängig |
| Organisatorische Voraussetzungen | 10 | 4 | 3 | 2 | C verlangt Rollen und Steuerung |
| **Gewichtete Summe** | **100** | **3,10** | **3,10** | **3,70** | |

**Wie stabil ist das Ergebnis?**

| Gewichtung | A | B | C |
|---|---|---|---|
| wie oben | 3,10 | 3,10 | **3,70** |
| alle Kriterien gleich | 3,22 | 3,11 | **3,56** |
| schneller Start: Voraussetzungen 20, Integration 10, Skalierbarkeit 5, Datenschutz 15, Wartbarkeit 5, Erweiterbarkeit 5, Kosten 20, Abhängigkeiten 5, Organisation 15 | **3,75** | 3,05 | 3,05 |

Das Ergebnis hängt also vom Zeithorizont ab: Für den Einstieg liegt A vorn, auf Dauer C.

## 4. Empfehlung: in Stufen von A nach C

1. **Stufe 1 (A):** Datenverträge, Prüfregeln, Katalog und Vergleichbarkeitsregeln für wenige aggregierte Quellen.
2. **Stufe 2:** Regeln und Katalog als eigenständige, wiederverwendbare Bausteine betreiben.
3. **Stufe 3 (C):** Schnittstellen dort ergänzen, wo Fachsysteme sie anbieten und eine Rechtsgrundlage besteht.

Warum nicht sofort C: Schnittstellen und Zuständigkeiten sind ungeklärt. Warum A nicht genügt: Der Demonstrator brauchte
schon für vier Dateien eigene Verträge. Datenverträge und Vergleichbarkeitsregeln aus Stufe 1 bleiben in C nutzbar.

Belege aus dem Demonstrator:
- Eine Datei schreibt den Namen des Landes uneinheitlich. Ohne Vertragsprüfung wäre M-V aus der Auswertung gefallen.
- Zwei Tabellen derselben Quelle meinen mit „Schülerzahl Klasse 5“ verschiedene Grundgesamtheiten.
- Ähnlich benannte Kompetenzbereiche gehören zu verschiedenen Rahmen. Ein gemeinsames Feld allein schafft keine Vergleichbarkeit.

## 5. Offene Fragen

**IT und Betrieb**
1. Welche Export- oder Programmierschnittstellen bietet ISY-MV, und enthält das Auswertungssystem Kompetenzdaten?
2. Gibt es ein dokumentiertes Datenmodell und einen landesweiten Schulschlüssel, den alle Systeme nutzen?
3. Wie ist der Stand der Ablösung von SIP durch ISY-MV?
4. Können LEO.MV, VERA und Lernlinie strukturierte Daten ausgeben? In welchem Format, auf welcher Ebene?
5. Welche Vorgaben gelten für Betrieb, Verschlüsselung, Protokollierung und Löschung?

**Fachreferate und IQ M-V**
6. Welche Entscheidungen sollen mit den Daten unterstützt werden, und auf welcher Ebene?
7. Auf welcher Skala berichtet LEO.MV, und sind Durchgänge untereinander verankert?
8. Welche Vergleiche sind fachlich gewollt, welche ausdrücklich nicht?
9. Wie hoch ist die Teilnahme an LEO.MV, und wer nimmt teil? Freiwilligkeit kann Ergebnisse verzerren.
10. Welche Daten benötigt die Schulentwicklungsplanung der Landkreise tatsächlich?

**Datenschutz und Recht**
11. Welche Rechtsgrundlage (Schulgesetz M-V, SchulDSVO M-V) trägt eine systemübergreifende Nutzung? Hier nicht geprüft.
12. Ist eine Auswertung ausschließlich aggregierter Daten ausreichend? Welche Mindestgruppengröße gilt?
13. Wer ist Verantwortlicher, und ist eine Datenschutz-Folgenabschätzung nötig?
