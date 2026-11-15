# CLI und Anwendungen V1–V4

Alle Befehle aus dem Repository-Hauptverzeichnis; `c1-lab --help` bzw. Unterbefehl `--help` zeigt Parameter. Standardquelle ist Demo; `inspect` erwartet Hardware. `--input` nur bei Replay. Demo ist für map bewegt, sonst stationär; `--moving`/`--no-moving` überschreibt das. Maximal 61 Demo-Scans, jeweils 500 Strahlen. Capture/Replay laufen ungedrosselt, Hardware wartet auf SDK-Daten.

## V1

```bash
c1-lab capture --scans 3 --output recordings/static-001
c1-lab scene --source replay --input recordings/static-001 --output recordings/scene-001
c1-lab scene --source replay --input recordings/static-001 --baseline recordings/scene-001/scene.json
c1-lab measure --input recordings/static-001/scan_000000.npz --indices 1 2
c1-lab export --source replay --input recordings/static-001 --output artifacts/points-001.csv
c1-lab filter --input recordings/static-001/scan_000000.npz --minimum .1 --maximum 6 --output recordings/filtered-001.npz
c1-lab bins --input recordings/static-001/scan_000000.npz --count 360
```

Scene/Export verwenden den ersten Scan. Scene speichert Bericht und Referenzsnapshot inklusive SHA256. Baseline-Snapshotänderung wird abgelehnt. Vergleich ist asymmetrischer nächster-Punkt-Abstand, keine Objektidentität/Poseschätzung; feste unveränderte Sensorpose vorausgesetzt. Punktmessung verwendet gültige native Indizes desselben rotierenden Scans. Zeit-/Objektbewegung innerhalb der Revolution kann verfälschen. Qualitätsfilter arbeitet auf dem rohen SDK-Byte, nicht kalibrierter Intensität.

Zeitliche Medianfilter sind zusätzlich als Python-API verfügbar: `from c1_lab.processing import temporal_median`; `temporal_median(list(ReplaySource('recordings/static-001')))` innerhalb eines geeigneten Offlineversuchs. Nur gleiche Winkelraster/Zeitdomains; bewegte Sensoren/Objekte können Trails erzeugen.

## V2/V3

```bash
c1-lab map --scans 12 --config configs/default.json --output recordings/map-001
c1-lab map --source replay --input recordings/map-001 --scans 12 --output recordings/replay-001
c1-lab landmarks --input recordings/map-001/landmarks.json --kind corner --confirmed
c1-lab landmarks --input recordings/map-001/landmarks.json --near 1 0 --radius .5
```

Native Punktdaten statt Winkelraster werden verarbeitet. Die lokale point-to-line-Registrierung verwendet gültige Nachbarn ohne Sprung über Löcher, paarweise Distanzsuche in begrenzten Chunks und robuste Restfehler. Das Verfahren ist für kleine Schritte/statische Szenen gedacht, ohne Multiskalen-/Bewegungsprädiktion. Kurze Innenraumszenen mit unterschiedlichen Wandrichtungen sind geeigneter als einzelne Wände oder lange symmetrische Korridore. Voraussetzungen und Drift an Hardware testen.

`--near X Y --radius R` filtert Landmarken in lokalen Kartenmetern nach Position; ohne --near wird nur nach Typ/Status gefiltert.

Landmarken sind Linien, Ecken und kleine Cluster mit klassen-/distanzbezogener Eins-zu-eins-Zuordnung; Linien zusätzlich mit Orientierungs-Gate. Linienzentren hängen vom sichtbaren Ausschnitt ab. IDs können sich durch Verdeckung, Symmetrie, Kartenfehler und veränderte Kontur teilen oder falsch zusammenfallen. Bestätigung ab drei Zuordnungen. Historie im Abschlussbericht auf 50 Beobachtungen je Landmarke begrenzt, vollständige Belege im Journal. Keine Objektklassen, globale optimale Zuordnung oder Cross-Session-IDs. Quellenbelege enthalten Datei, native Scanpunktindizes beziehungsweise unterstützende Linien, Scan-Fingerabdruck und Pose. Ecken verweisen auf die aus demselben Scan rekonstruierbaren Unterstützungsgeraden.

Gridzustände -1 unbekannt, 0 frei, 100 belegt. Aktuell nicht eindeutige Log-Odds bleiben unbekannt. `grid.npz` enthält auch seen/log_odds. PGM wird vertikal gedreht exportiert, damit ROS-Kartenursprung unten links stimmt. Weltursprung ist erster Sensor, kein globales/geografisches Bezugssystem. Separate ROS-SLAM-Posen korrigieren diese Karte nicht automatisch. `--no-landmarks` überspringt Landmarkenfusion.

## V4 offline

```bash
c1-lab plan --input recordings/map-001/grid.npz --start .5 .5 --goal 2 2 --radius .2 --output artifacts/plan-001.json
```

Start/Ziel in Kartenmetern. Kreisfootprint mit Radius; Inflation behandelt Hindernisse, unbekannte Zellen und Rand konservativ. Zellhalbdiagonale wird zusätzlich berücksichtigt. A* nutzt vier Nachbarn, keine diagonalen Abkürzungen. Kein Pfad ist ein gültiges Ergebnis. Unbekannte/footprint-blockierte Start-/Zielzellen führen zu Fehler. Das ist keine geprüfte Navigation; Rotations-/Fahrdynamik, Geschwindigkeiten und ein echter Robotercontroller fehlen bewusst. Montageversatz/Robotergeometrie müssen für spätere Nutzung korrekt eingebunden werden.

`benchmark` berichtet Hostdurchsatz, Zeitintervalle, beobachtete Sequenzlücken und HIT-Anteil. Hostempfangsintervalle sind keine präzise Motorfrequenz-/Punktzeitmessung. SDK-Bridge-Sequenznummern sind Host-Zähler und können Transport-/Sensorausfälle nicht vollständig quantifizieren. Referenzgenauigkeit/Messstreuung sind eigene physische Versuche.

Exitcodes: 0 erfolgreiche Verarbeitung, 2 Eingabe-/Gerätefehler, erkannter Trackingverlust oder kein Offlinepfad, 130 Unterbrechung. Ein fehlerfreier Lauf beweist keine Herstellerkonformität.
