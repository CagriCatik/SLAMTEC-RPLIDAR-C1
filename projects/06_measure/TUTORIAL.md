# 06 — Punktmessung

## Ziel und Code

Zwei gültige native HIT-Indizes desselben Scans. Vergleiche bekannte Strecke; kein Höhen-/Volumenmaß und keine garantierte Unsicherheit.

Dieser Ordner enthält die Anleitung. Gemeinsamer ausführbarer Code: **geometry.py / points; cli.py / measure**, keine duplizierten Kameras-/Scannerskripte.

## Ausführen

Alle Befehle im Repository-Hauptverzeichnis, Pythonumgebung aktiviert. Demo benötigt NumPy, Viewer zusätzlich Matplotlib; Hardware benötigt Bridge/Adapter, ROS seine Systempakete.

```bash
c1-lab capture --scans 1 --output recordings/tutorial-06
c1-lab measure --input recordings/tutorial-06/scan_000000.npz --indices 1 2
```

Erwartung: JSON mit zwei nativen Scanindizes, deren kartesischen Punkten, euklidischem Abstand und Scan-Fingerabdruck. Details zu den Feldern und Formaten: [Anwendungsreferenz](../../docs/applications.md).

## Experiment und Grenzen

Miss zwei bekannte Wandpunkte. Wähle danach einen ungültigen Index und prüfe, dass statt eines falschen Abstands ein Fehler entsteht. Ein erfolgreicher Programmlauf beweist keine Hardwaregenauigkeit.

Bei fehlenden Paketen/Portzugriff der [Einrichtung](../../docs/setup.md) folgen; neue Ausgabenamen verwenden. Geometrie-/Zeitfehler nicht durch ungeprüfte Interpolation oder erfundene Posen kaschieren.

[Zurück](../05_geometry/TUTORIAL.md) · [Weiter](../07_clusters/TUTORIAL.md) · [Index](../../TUTORIAL_INDEX.md)
