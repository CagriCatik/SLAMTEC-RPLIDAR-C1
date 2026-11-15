# 14 — SLAM-Anbindung

## Ziel und Code

Externe gültige Odometrie/TF und SLAM Toolbox sind Voraussetzung. Keine künstliche Identitäts-Odometrie einsetzen. Kein hier ausgeführter ROS-Lauf.

Dieser Ordner enthält die Anleitung. Gemeinsamer ausführbarer Code: **ros2/slam.launch.py, ros2/slam.yaml**, keine duplizierten Kameras-/Scannerskripte.

## Ausführen

Alle Befehle im Repository-Hauptverzeichnis, Pythonumgebung aktiviert. Demo benötigt NumPy, Viewer zusätzlich Matplotlib; Hardware benötigt Bridge/Adapter, ROS seine Systempakete.

```bash
ros2 launch "$PWD/ros2/slam.launch.py"
```

Erwartung: SLAM-Toolbox-Start mit eigener Parameterdatei; ohne echte Odometrie/TF kein gültiger Mapping-Nachweis. Details zu den Feldern und Formaten: [Anwendungsreferenz](../../docs/applications.md).

## Experiment und Grenzen

Prüfe zuerst odom->base_link->laser zeitlich und geometrisch. Miss später eine Referenzrunde und vergleiche Drift/Loop Closure. Ein erfolgreicher Programmlauf beweist keine Hardwaregenauigkeit.

Bei fehlenden Paketen/Portzugriff der [Einrichtung](../../docs/setup.md) folgen; neue Ausgabenamen verwenden. Geometrie-/Zeitfehler nicht durch ungeprüfte Interpolation oder erfundene Posen kaschieren.

[Zurück](../13_ros2/TUTORIAL.md) · [Weiter](../15_planning/TUTORIAL.md) · [Index](../../TUTORIAL_INDEX.md)
