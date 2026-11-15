# 10 — Scan Matching

## Ziel und Code

Relative vorige→aktuelle Sensorpose; Weltpose wird mit Inverse verkettet. Einzelwände und Parallelgeometrie können unzureichend beobachtbar sein.

Dieser Ordner enthält die Anleitung. Gemeinsamer ausführbarer Code: **odometry.py**, keine duplizierten Kameras-/Scannerskripte.

## Ausführen

Alle Befehle im Repository-Hauptverzeichnis, Pythonumgebung aktiviert. Demo benötigt NumPy, Viewer zusätzlich Matplotlib; Hardware benötigt Bridge/Adapter, ROS seine Systempakete.

```bash
c1-lab map --scans 5 --no-landmarks --output recordings/tutorial-10
```

Erwartung: Fünf Scanaufnahmen, Trajektorie/Statusjournal und eine lokale Karte; bei erkanntem Verlust keine neuen Posen. Details zu den Feldern und Formaten: [Anwendungsreferenz](../../docs/applications.md).

## Experiment und Grenzen

Vergleiche die gespeicherten Posen gegen DemoSource.pose_at. Versuche eine einzelne Wand; unbestimmbare Bewegung muss verworfen werden. Ein erfolgreicher Programmlauf beweist keine Hardwaregenauigkeit.

Bei fehlenden Paketen/Portzugriff der [Einrichtung](../../docs/setup.md) folgen; neue Ausgabenamen verwenden. Geometrie-/Zeitfehler nicht durch ungeprüfte Interpolation oder erfundene Posen kaschieren.

[Zurück](../09_sectors/TUTORIAL.md) · [Weiter](../11_mapping/TUTORIAL.md) · [Index](../../TUTORIAL_INDEX.md)
