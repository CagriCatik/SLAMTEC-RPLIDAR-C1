# 13 — ROS 2 und RViz

## Ziel und Code

Offizielles Paket und kompatibles ROS nötig. Nur Syntax/API geprüft. Scan-Raster, QoS, Zeitfelder und Montage-TF separat abnehmen.

Dieser Ordner enthält die Anleitung. Gemeinsamer ausführbarer Code: **ros2/c1.launch.py**, keine duplizierten Kameras-/Scannerskripte.

## Ausführen

Alle Befehle im Repository-Hauptverzeichnis, Pythonumgebung aktiviert. Demo benötigt NumPy, Viewer zusätzlich Matplotlib; Hardware benötigt Bridge/Adapter, ROS seine Systempakete.

```bash
ros2 launch "$PWD/ros2/c1.launch.py"
```

Erwartung: Der offizielle ROS-Treiber soll /scan publizieren; Topic/QoS/Frame und RViz sind am echten Aufbau zu prüfen. Details zu den Feldern und Formaten: [Anwendungsreferenz](../../docs/applications.md).

## Experiment und Grenzen

Zeige /scan und den laser-Frame in RViz. Vergleiche Rasterauflösung und Inf-Werte mit nativen Bridge-Daten; nicht als identische Rohdaten behandeln. Ein erfolgreicher Programmlauf beweist keine Hardwaregenauigkeit.

Bei fehlenden Paketen/Portzugriff der [Einrichtung](../../docs/setup.md) folgen; neue Ausgabenamen verwenden. Geometrie-/Zeitfehler nicht durch ungeprüfte Interpolation oder erfundene Posen kaschieren.

[Zurück](../12_landmarks/TUTORIAL.md) · [Weiter](../14_slam/TUTORIAL.md) · [Index](../../TUTORIAL_INDEX.md)
