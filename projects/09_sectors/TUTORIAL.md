# 09 — Sektorbeobachtung

## Ziel und Code

Vorderer Sektor zeigt nächsten HIT und unbekannten Anteil. Kein HIT bedeutet nicht null Meter und nicht automatisch freie Fahrt.

Dieser Ordner enthält die Anleitung. Gemeinsamer ausführbarer Code: **processing.py / sector**, keine duplizierten Kameras-/Scannerskripte.

## Ausführen

Alle Befehle im Repository-Hauptverzeichnis, Pythonumgebung aktiviert. Demo benötigt NumPy, Viewer zusätzlich Matplotlib; Hardware benötigt Bridge/Adapter, ROS seine Systempakete.

```bash
c1-lab scene
```

Erwartung: front_sector enthält HIT-Mindestabstand oder null sowie unbekannten und expliziten CLEAR-Anteil. Details zu den Feldern und Formaten: [Anwendungsreferenz](../../docs/applications.md).

## Experiment und Grenzen

Wähle einen Sektor ohne gültigen Treffer. Unterscheide nearest_hit_m=null von gemessenem Freiraum oder einem Hindernis bei null Metern. Ein erfolgreicher Programmlauf beweist keine Hardwaregenauigkeit.

Bei fehlenden Paketen/Portzugriff der [Einrichtung](../../docs/setup.md) folgen; neue Ausgabenamen verwenden. Geometrie-/Zeitfehler nicht durch ungeprüfte Interpolation oder erfundene Posen kaschieren.

[Zurück](../08_lines/TUTORIAL.md) · [Weiter](../10_odometry/TUTORIAL.md) · [Index](../../TUTORIAL_INDEX.md)
