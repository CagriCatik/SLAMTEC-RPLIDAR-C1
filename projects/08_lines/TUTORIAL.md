# 08 — Linien und Ecken

## Ziel und Code

RANSAC/TLS und Schnittpunkte nahe Enden. Untersuche Ausreißer/kollineare Lücken; ein Liniensegment beweist keine durchgehende Wand oder Objektklasse.

Dieser Ordner enthält die Anleitung. Gemeinsamer ausführbarer Code: **processing.py / lines, corners**, keine duplizierten Kameras-/Scannerskripte.

## Ausführen

Alle Befehle im Repository-Hauptverzeichnis, Pythonumgebung aktiviert. Demo benötigt NumPy, Viewer zusätzlich Matplotlib; Hardware benötigt Bridge/Adapter, ROS seine Systempakete.

```bash
c1-lab scene
```

Erwartung: JSON-Liniennormalen, Abstand zum Ursprung, Segmentenden, Restfehler und nahe Endpunkt-Schnittpunkte. Details zu den Feldern und Formaten: [Anwendungsreferenz](../../docs/applications.md).

## Experiment und Grenzen

Füge der Demopunktmenge Ausreißer hinzu und variiere den RANSAC-Schwellwert. Vergleiche Linien-RMSE und Eckhypothesen mit den bekannten Wänden. Ein erfolgreicher Programmlauf beweist keine Hardwaregenauigkeit.

Bei fehlenden Paketen/Portzugriff der [Einrichtung](../../docs/setup.md) folgen; neue Ausgabenamen verwenden. Geometrie-/Zeitfehler nicht durch ungeprüfte Interpolation oder erfundene Posen kaschieren.

[Zurück](../07_clusters/TUTORIAL.md) · [Weiter](../09_sectors/TUTORIAL.md) · [Index](../../TUTORIAL_INDEX.md)
