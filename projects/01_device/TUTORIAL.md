# 01 — Gerätecheck

## Ziel und Code

Hardware + gebauter SDK-Adapter nötig. Modell, Serial, Gesundheit und Modi lesen, ohne Motorstart. Firmware-/Hardwarecode und R2-Typenschild abgleichen.

Dieser Ordner enthält die Anleitung. Gemeinsamer ausführbarer Code: **drivers.py und drivers/c1_bridge.cpp**, keine duplizierten Kameras-/Scannerskripte.

## Ausführen

Alle Befehle im Repository-Hauptverzeichnis, Pythonumgebung aktiviert. Demo benötigt NumPy, Viewer zusätzlich Matplotlib; Hardware benötigt Bridge/Adapter, ROS seine Systempakete.

```bash
c1-lab inspect --port /dev/ttyUSB0
```

Erwartung: JSON-Gerätebericht mit Modell-/Firmware-/Hardwarecode, Gesundheitsstatus und angebotenen Scanmodi. Ohne Gerät ein verständlicher Fehler, kein Demogerät. Details zu den Feldern und Formaten: [Anwendungsreferenz](../../docs/applications.md).

## Experiment und Grenzen

Vergleiche Typenschild, angezeigte C1-Modellbeschreibung und verfügbare Modi. Verändere den Port absichtlich und prüfe die Fehlermeldung. Ein erfolgreicher Programmlauf beweist keine Hardwaregenauigkeit.

Bei fehlenden Paketen/Portzugriff der [Einrichtung](../../docs/setup.md) folgen; neue Ausgabenamen verwenden. Geometrie-/Zeitfehler nicht durch ungeprüfte Interpolation oder erfundene Posen kaschieren.

[Zurück](../../README.md) · [Weiter](../02_viewer/TUTORIAL.md) · [Index](../../TUTORIAL_INDEX.md)
