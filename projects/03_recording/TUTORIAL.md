# 03 — Aufnahme und Replay

## Ziel und Code

Versioniertes NPZ ohne Pickle. Native Arrays und Zeitmetadaten erhalten. Vorhandene Ausgaben werden nicht überschrieben.

Dieser Ordner enthält die Anleitung. Gemeinsamer ausführbarer Code: **storage.py, sources.py**, keine duplizierten Kameras-/Scannerskripte.

## Ausführen

Alle Befehle im Repository-Hauptverzeichnis, Pythonumgebung aktiviert. Demo benötigt NumPy, Viewer zusätzlich Matplotlib; Hardware benötigt Bridge/Adapter, ROS seine Systempakete.

```bash
c1-lab capture --scans 3 --output recordings/tutorial-03
c1-lab scene --source replay --input recordings/tutorial-03
```

Erwartung: Drei scan_*.npz-Dateien; danach ein JSON-Szenenbericht aus der Wiedergabe. Details zu den Feldern und Formaten: [Anwendungsreferenz](../../docs/applications.md).

## Experiment und Grenzen

Spiele dieselbe Sitzung zweimal ab. Vergleiche Fingerabdrücke und Berichtsfelder; ein neuer Quellpfad darf keine Messwerte verändern. Ein erfolgreicher Programmlauf beweist keine Hardwaregenauigkeit.

Bei fehlenden Paketen/Portzugriff der [Einrichtung](../../docs/setup.md) folgen; neue Ausgabenamen verwenden. Geometrie-/Zeitfehler nicht durch ungeprüfte Interpolation oder erfundene Posen kaschieren.

[Zurück](../02_viewer/TUTORIAL.md) · [Weiter](../04_filters/TUTORIAL.md) · [Index](../../TUTORIAL_INDEX.md)
