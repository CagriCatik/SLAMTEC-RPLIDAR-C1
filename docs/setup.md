# Einrichtung

Referenzziel: Linux, Ubuntu 24.04 / Python 3.12; Kern-CI unter 3.11–3.13. Der SDK-Hersteller führt weitere Plattformen auf; unser Build-/Prozessadapter ist derzeit nur unter Linux geprüft. Keine pauschale macOS-/Windows-/Jazzy-Freigabe ableiten.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python scripts/build_bridge.py
c1-lab inspect --port /dev/ttyUSB0
```

Der Build pinnt SDK `99478e5fb90de3b4a6db0080acacd373f8b36869`, baut nur die Bibliothek und unsere Bridge, keine Vendor-Demos. Für bereits lokal vorhandenes sauberes SDK: `python scripts/build_bridge.py --sdk /absoluter/pfad/rplidar_sdk`. Unpassende Revisionen werden abgelehnt. Compiler, SDK-Commit und SDK-Lizenz werden in artifacts gespeichert. Buildausgaben können erneut gebaut werden; Versuchsdateien werden exklusiv angelegt.

Geeigneten SLAMTEC-Adapter und ein Datenkabel verwenden. Tatsächlichen Port sowie Linux-Gruppen-/udev-Zugriff nach Herstellerunterlagen einrichten. Keine pauschalen chmod-777-Regeln. Bei offener Bare-Module-Verdrahtung müssen Versorgung und Pinbelegung aus dem zur Revision passenden Herstellerhandbuch verifiziert werden; hier werden keine ungeprüften Pin-/Spannungswerte vorgeschrieben.

`inspect` liest Gerätekennung, Firmware-/Hardwarecode, Serial, Gesundheit und angebotene Modi. Es startet den Motor nicht. Ein erfolgreicher Diagnoseaufruf bedeutet auslesbar, nicht automatisch gesund. Scanbefehle verlangen im Bridge-Code gesunden Status und eine C1-Modellbeschreibung. Falls die SDK-Modellbeschreibung unbekannt ist, zuerst SDK/Typenschild klären; nicht ungeprüft auf ein anderes Modell ausweichen.

```bash
c1-lab capture --source hardware --port /dev/ttyUSB0 --scans 100 --output recordings/session-001
c1-lab benchmark --source hardware --scans 100 --output artifacts/health-001.json
python -m pip install -e '.[viewer]'
c1-lab view --source replay --input recordings/session-001 --scans 100
```

Baudrate ist in der Bridge C1-spezifisch 460800; der Bridge-Aufruf bietet bei bewusster direkter Verwendung ein Baudargument. Scanmodus-ID mit `c1-lab inspect` ermitteln und optional `--mode ID` angeben. Ohne ID wählt das SDK den typischen Modus, nicht einfach den ersten Eintrag.

Fehler: Port nicht vorhanden/keine Rechte → Verbindung prüfen; fehlender Bridge-Build → Build ausführen; Gesundheitsfehler → Herstellerdiagnose; Timeout/Abbruch → SDK-Scan und Motor werden beim regulären Cleanup gestoppt. SIGKILL, Betriebssystem-/USB-/Stromausfall erlauben keine Softwaregarantie für physisches Stoppen. Es gibt keine automatischen Firmwareupdates oder Resets.

Viewer benötigt Matplotlib und Desktop. Headless-Export: `MPLBACKEND=Agg c1-lab view --headless --scans 1 --save artifacts/scan.png`. SDK-/ROS-Zugänge nicht gleichzeitig mit der Standalone-Bridge auf demselben Port öffnen.
