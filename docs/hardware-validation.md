# Hardware-Abnahme — offen

Pro Versuch speichern: Datum, Modell/Typenschildrevision, Serial, Firmware, SDK-/Treiber-Commit, OS/Kernel, Compiler/Python, Adapter/Port, Versorgung nach verifizierter Dokumentation, Modus, tatsächliche Empfangsintervalle, Geometrie, Oberflächen, Licht und unabhängiges Referenzmessmittel.

1. R2-Unterlagen: Datenblatt/Handbuch/Pinout/Versorgung und Winkelzeichnung vollständig zur Hardware zuordnen. Noch offen.
2. Diagnose: Geräte-/Gesundheitsdaten/Modi lesen; falscher Port/Gesundheitsfehler muss verständlich scheitern.
3. Native Winkel prüfen: bekannte Ziele vorne/links/hinten/rechts; physische Nullrichtung und pi-native-Konvention bestätigen. Rohwerte erhalten.
4. Entfernungen: mehrere Referenzdistanzen und Oberflächen, u. a. unterschiedliche Reflexion/Winkel. Bias, Streuung, Ausfälle und Bedingungen getrennt bewerten; Auflösung ist keine Genauigkeit.
5. Revolution/Zeiten: Punktzahl, Modus, Empfangszeiten, Abdeckung/Lücken und SDK-Flags prüfen. Keine präzisen Punktzeiten aus groben Hostzeiten ableiten.
6. V1: Linien/Ecken/Cluster an bekannten Konturen; Scan über Winkelgrenze, Löcher, Ausreißer und Teilscans prüfen; Zweipunktmessung gegen Referenz.
7. V2: langsam bekannte Strecke/Rotation fahren oder Sensor bewegen; Maßstab, Transformationsrichtung, Drift und Trackingverlust kontrollieren. Einzelwand/Korridor/Symmetrie separat testen.
8. Occupancy: fehlende Rückgabe und Nahbereich unbekannt; bestätigte Ziele belegt; kein künstliches Randhindernis; Kartenursprung/PGM-Ausrichtung bestätigen.
9. V3: Merkmale wiederbeobachten, gleiche Geometrie an mehreren Orten/Verdeckung testen; IDs und native Belege prüfen. Keine Objektklassifikation behaupten.
10. Replay: ursprüngliche Aufnahmen unverändert erneut auswerten; Konfiguration und Versionsstand dokumentieren. Veränderte Baseline muss scheitern.
11. Cleanup: regulären Abbruch, Lese-/Prozessfehler und Neustart untersuchen; Motorstop physisch bestätigen. Kein physischer Stopnachweis für SIGKILL/Verbindungs-/Stromausfall.
12. ROS: LaserScan-Raster, QoS, Scanzeitfelder, laser-TF, korrekte Robotermontage und echte Odometrie prüfen. SLAM/Loop Closure und Bag-Replay getrennt abnehmen.
13. V4: Pfade offline/Simulation auf bekannte Karte mit gemessenem Footprint; reale Steuerung bleibt eigener Auftrag mit passendem Robotikaufbau.

Erst nach tatsächlicher Prüfung Nachweise in capabilities.md ergänzen. Die erste Softwareversion ist keine Navigations- oder Herstellerfreigabe.
