# 05 — Geometrie und Montage

## Ziel und Code

Meter, Radiant, x vorwärts/y links. Native Q14-Konvention und Montage getrennt prüfen. Eine Posematrix transformiert Sensorpunkte in den lokalen Kartenrahmen.

Dieser Ordner enthält die Anleitung. Gemeinsamer ausführbarer Code: **geometry.py**, keine duplizierten Kameras-/Scannerskripte.

## Ausführen

Alle Befehle im Repository-Hauptverzeichnis, Pythonumgebung aktiviert. Demo benötigt NumPy, Viewer zusätzlich Matplotlib; Hardware benötigt Bridge/Adapter, ROS seine Systempakete.

```bash
c1-lab scene
```

Erwartung: JSON mit Linien, Ecken, Clustern und Sektormessung. Prüfe x/y-Vorzeichen an bekannten Demowänden. Details zu den Feldern und Formaten: [Anwendungsreferenz](../../docs/applications.md).

## Experiment und Grenzen

Transformiere einen Punkt mit pose_matrix([1,2,pi/2]) und prüfe die inverse Rücktransformation. Hardwaremontage anschließend unabhängig vermessen. Ein erfolgreicher Programmlauf beweist keine Hardwaregenauigkeit.

Bei fehlenden Paketen/Portzugriff der [Einrichtung](../../docs/setup.md) folgen; neue Ausgabenamen verwenden. Geometrie-/Zeitfehler nicht durch ungeprüfte Interpolation oder erfundene Posen kaschieren.

[Zurück](../04_filters/TUTORIAL.md) · [Weiter](../06_measure/TUTORIAL.md) · [Index](../../TUTORIAL_INDEX.md)
