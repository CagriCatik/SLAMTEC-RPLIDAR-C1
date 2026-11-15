# 16 — Qualität und Laufzeit

## Ziel und Code

Hostdurchsatz getrennt von Quelle/Rotation bewerten. Referenzgenauigkeit, Zeitstreuung und Oberflächen müssen physisch gemessen werden.

Dieser Ordner enthält die Anleitung. Gemeinsamer ausführbarer Code: **applications.py / benchmark**, keine duplizierten Kameras-/Scannerskripte.

## Ausführen

Alle Befehle im Repository-Hauptverzeichnis, Pythonumgebung aktiviert. Demo benötigt NumPy, Viewer zusätzlich Matplotlib; Hardware benötigt Bridge/Adapter, ROS seine Systempakete.

```bash
c1-lab benchmark --scans 30
```

Erwartung: JSON mit Hostdurchsatz, Quellintervall, Zeitdomains, Sequenzlücken und gültigem HIT-Anteil. Details zu den Feldern und Formaten: [Anwendungsreferenz](../../docs/applications.md).

## Experiment und Grenzen

Vergleiche Demo-/Replay-/Hardwaredurchsatz. Wiederhole mit anderer Hostlast; leite daraus keine veränderte Sensor-Motorfrequenz ab. Ein erfolgreicher Programmlauf beweist keine Hardwaregenauigkeit.

Bei fehlenden Paketen/Portzugriff der [Einrichtung](../../docs/setup.md) folgen; neue Ausgabenamen verwenden. Geometrie-/Zeitfehler nicht durch ungeprüfte Interpolation oder erfundene Posen kaschieren.

[Zurück](../15_planning/TUTORIAL.md) · [Weiter](../../docs/hardware-validation.md) · [Index](../../TUTORIAL_INDEX.md)
