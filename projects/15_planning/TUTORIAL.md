# 15 — Robotikvorbereitung offline

## Ziel und Code

Kreisfootprint, Inflation einschließlich unbekannter Bereiche und Rand, A* mit vier Nachbarn. Kein Aktuator-/Fahrbefehl.

Dieser Ordner enthält die Anleitung. Gemeinsamer ausführbarer Code: **planning.py**, keine duplizierten Kameras-/Scannerskripte.

## Ausführen

Alle Befehle im Repository-Hauptverzeichnis, Pythonumgebung aktiviert. Demo benötigt NumPy, Viewer zusätzlich Matplotlib; Hardware benötigt Bridge/Adapter, ROS seine Systempakete.

```bash
c1-lab map --scans 12 --output recordings/tutorial-15
c1-lab plan --input recordings/tutorial-15/grid.npz --start .5 .5 --goal 2 2 --radius .2 --output artifacts/tutorial-15-plan.json
```

Erwartung: JSON mit Offlinepfad in Kartenmetern oder no_path; kein Roboter-/Aktuatorzugriff. Details zu den Feldern und Formaten: [Anwendungsreferenz](../../docs/applications.md).

## Experiment und Grenzen

Erhöhe den Footprint-Radius und prüfe, ob Engstellen blockiert werden. Unbekannte Start-/Zielbereiche müssen abgewiesen werden. Ein erfolgreicher Programmlauf beweist keine Hardwaregenauigkeit.

Bei fehlenden Paketen/Portzugriff der [Einrichtung](../../docs/setup.md) folgen; neue Ausgabenamen verwenden. Geometrie-/Zeitfehler nicht durch ungeprüfte Interpolation oder erfundene Posen kaschieren.

[Zurück](../14_slam/TUTORIAL.md) · [Weiter](../16_benchmark/TUTORIAL.md) · [Index](../../TUTORIAL_INDEX.md)
