# 04 — Filterlabor

## Ziel und Code

Verworfene Punkte werden UNKNOWN. Keine Lochfüllung. Zeitlicher Median als Python-API nur bei gleicher Geometrie und steigender Zeit; keine Bewegungsentzerrung.

Dieser Ordner enthält die Anleitung. Gemeinsamer ausführbarer Code: **processing.py / filter_scan, temporal_median, angular_bins**, keine duplizierten Kameras-/Scannerskripte.

## Ausführen

Alle Befehle im Repository-Hauptverzeichnis, Pythonumgebung aktiviert. Demo benötigt NumPy, Viewer zusätzlich Matplotlib; Hardware benötigt Bridge/Adapter, ROS seine Systempakete.

```bash
c1-lab capture --scans 1 --output recordings/tutorial-04
c1-lab filter --input recordings/tutorial-04/scan_000000.npz --maximum 6 --output recordings/tutorial-04-filtered.npz
```

Erwartung: Ein nativer Snapshot und ein neuer gefilterter Snapshot; verworfene Distanzen bleiben als Rohwerte erhalten, ihr Status wird UNKNOWN. Details zu den Feldern und Formaten: [Anwendungsreferenz](../../docs/applications.md).

## Experiment und Grenzen

Reduziere maximum von 6 auf 2 m und vergleiche HIT/UNKNOWN-Anteile. Beobachte, dass keine künstlichen freien Strahlen entstehen. Ein erfolgreicher Programmlauf beweist keine Hardwaregenauigkeit.

Bei fehlenden Paketen/Portzugriff der [Einrichtung](../../docs/setup.md) folgen; neue Ausgabenamen verwenden. Geometrie-/Zeitfehler nicht durch ungeprüfte Interpolation oder erfundene Posen kaschieren.

[Zurück](../03_recording/TUTORIAL.md) · [Weiter](../05_geometry/TUTORIAL.md) · [Index](../../TUTORIAL_INDEX.md)
