# 02 — Liveviewer

## Ziel und Code

Viewer-Extra installieren; kartesische Darstellung mit Linien. --polar zeigt Polaransicht. Beide Darstellungen verwenden Kernwinkel, nicht ungeprüfte Native-Achsen.

Dieser Ordner enthält die Anleitung. Gemeinsamer ausführbarer Code: **viewer.py**, keine duplizierten Kameras-/Scannerskripte.

## Ausführen

Alle Befehle im Repository-Hauptverzeichnis, Pythonumgebung aktiviert. Demo benötigt NumPy, Viewer zusätzlich Matplotlib; Hardware benötigt Bridge/Adapter, ROS seine Systempakete.

```bash
c1-lab view --scans 30
```

Erwartung: Kartesisches Fenster mit gültigen Scanpunkten und gefitteten Linien; --polar öffnet dieselben Messungen als Winkel/Distanz. Details zu den Feldern und Formaten: [Anwendungsreferenz](../../docs/applications.md).

## Experiment und Grenzen

Vergleiche Polar- und kartesische Ansicht; untersuche die fehlenden Strahlen der Demo und stelle sicher, dass sie nicht als Nullabstand eingezeichnet werden. Ein erfolgreicher Programmlauf beweist keine Hardwaregenauigkeit.

Bei fehlenden Paketen/Portzugriff der [Einrichtung](../../docs/setup.md) folgen; neue Ausgabenamen verwenden. Geometrie-/Zeitfehler nicht durch ungeprüfte Interpolation oder erfundene Posen kaschieren.

[Zurück](../01_device/TUTORIAL.md) · [Weiter](../03_recording/TUTORIAL.md) · [Index](../../TUTORIAL_INDEX.md)
