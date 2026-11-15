# Funktionsmatrix 0.1.0

Softwareprüfung ist keine Hardwareabnahme. Wo keine echte Messung vorliegt, bleibt der Status offen.

| Fähigkeit | Implementiert | Softwaregeprüft | Integriert geprüft | Hardware |
|---|---|---|---|---|
| Native Aufnahme/Diagnose/Scanmodi | SDK-Bridge + Prozessadapter | Dekodierung, Fehler/Cleanup simuliert | SDK/Bridge Linux gebaut, fehlender Port sauber abgewiesen | Offen |
| Exaktes C1M1-R2-Revisions-/Elektrikprofil | Quellenindex/Eckdaten | Unvollständige PDFs gekennzeichnet | Vollständiger Abgleich offen | Offen |
| Polar-/Kartesisch-Viewer | Matplotlib | Headless-Render | PNGs visuell geprüft | Offen |
| Aufnahme/Replay/Referenzvergleich | NPZ/JSON/Fingerabdruck | CLI und Roundtrip | Synthetische Ende-zu-Ende-Kette | Offen |
| Filter/Bins/zeitlicher Median | Kern/CLI bzw. Python-API | Ungültige Werte/Zeiten/Lücken | Synthetisch | Offen |
| Punktmessung/Sektoren/Cluster/Linien/Ecken | V1 | Achsen, Wrap, Ausreißer/Degeneration | Synthetisch | Offen |
| SE2-Odometrie/Trackingverlust | V2 | Bekannte Posen, Zeit-/Geometriefehler | Demo/Replay | Offen |
| Frei/Belegt/Unbekannt, Blindzone | V2 | Strahlen, Endpunkte, Grenzen, Export | Demo/Replay | Offen |
| Geometrische Landmarken | V3 | Quellenbezug, Wiederbeobachtung, Duplikate | Synthetisch | Offen |
| Footprint/Inflation/A* | V4 offline | Unbekannt/Engstellen/Rand/Pfad | Gespeicherte Demokarte | Kein Fahrbetrieb |
| ROS-2-Treiber/RViz | Launch/Anleitung | Syntax/API-Abgleich | ROS/Jazzy-Lauf offen | Offen |
| SLAM Toolbox/Loop Closure | Externer Launch | API-Abgleich | Externe Odometrie/TF und ROS nötig | Offen |
| Deskew/Punktzeiten | Nicht implementiert | Kein Zeitnachweis erfunden | Nicht geprüft | Offen |
| Gemessene Reflektivität/2.5D/Höhe | Nicht interpretiert | Rohquality/Flags erhalten | Bedeutungen offen | Offen |
| Qualitätsbenchmark | Host-/Scanstatistik | Zeit-/Sequenzlogik | Demo | Referenzmessung offen |
| Autonome Navigation/Sensorfusion | Nicht implementiert | V4 nur Offlineplanung | Nicht geprüft | Offen |

Nächste sinnvolle Schritte: echte C1-Baseline aufnehmen, vollständige Revisionsunterlagen abgleichen, Host-/Gerätezeitqualität untersuchen, robuste Registrierung/Loop-Closure-Integration und reale Roboter-TFs validieren. Keine dieser offenen Aufgaben wird durch synthetische Zahlen als erledigt markiert.
