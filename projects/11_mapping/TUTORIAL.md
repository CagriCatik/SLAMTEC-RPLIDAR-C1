# 11 — Lokale Karte

## Ziel und Code

Log-Odds und frei/belegt/unbekannt; Blindzone bleibt unbekannt. Unbekannte Rückgaben verändern keine Zellen. Trackingverlust stoppt weitere Fusion.

Dieser Ordner enthält die Anleitung. Gemeinsamer ausführbarer Code: **mapping.py, applications.py**, keine duplizierten Kameras-/Scannerskripte.

## Ausführen

Alle Befehle im Repository-Hauptverzeichnis, Pythonumgebung aktiviert. Demo benötigt NumPy, Viewer zusätzlich Matplotlib; Hardware benötigt Bridge/Adapter, ROS seine Systempakete.

```bash
c1-lab map --scans 12 --output recordings/tutorial-11
```

Erwartung: Occupancy Grid als grid.npz sowie map.pgm/map.yaml und nachvollziehbare Sensortrajektorie. Details zu den Feldern und Formaten: [Anwendungsreferenz](../../docs/applications.md).

## Experiment und Grenzen

Prüfe Zellen vor und hinter einem bekannten Ziel, innerhalb der Blindzone und hinter einer fehlenden Rückgabe. Dokumentiere unbekannte Bereiche. Ein erfolgreicher Programmlauf beweist keine Hardwaregenauigkeit.

Bei fehlenden Paketen/Portzugriff der [Einrichtung](../../docs/setup.md) folgen; neue Ausgabenamen verwenden. Geometrie-/Zeitfehler nicht durch ungeprüfte Interpolation oder erfundene Posen kaschieren.

[Zurück](../10_odometry/TUTORIAL.md) · [Weiter](../12_landmarks/TUTORIAL.md) · [Index](../../TUTORIAL_INDEX.md)
