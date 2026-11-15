# 07 — Cluster

## Ziel und Code

Winkel- und 3D-freie 2D-Abstandsnachbarschaft. Ungültige Punkte unterbrechen Gruppen; nur vollständige Revolution darf an der Winkelgrenze verbunden werden.

Dieser Ordner enthält die Anleitung. Gemeinsamer ausführbarer Code: **processing.py / clusters**, keine duplizierten Kameras-/Scannerskripte.

## Ausführen

Alle Befehle im Repository-Hauptverzeichnis, Pythonumgebung aktiviert. Demo benötigt NumPy, Viewer zusätzlich Matplotlib; Hardware benötigt Bridge/Adapter, ROS seine Systempakete.

```bash
c1-lab scene
```

Erwartung: JSON-Cluster mit originalen Messpunktindizes, Schwerpunkt sichtbarer Punkte und sichtbarer XY-Ausdehnung. Details zu den Feldern und Formaten: [Anwendungsreferenz](../../docs/applications.md).

## Experiment und Grenzen

Erzeuge im Python-Kern gültige Nachbarn beiderseits der Winkelgrenze und setze full_revolution abwechselnd true/false. Teilscans dürfen nicht verbunden werden. Ein erfolgreicher Programmlauf beweist keine Hardwaregenauigkeit.

Bei fehlenden Paketen/Portzugriff der [Einrichtung](../../docs/setup.md) folgen; neue Ausgabenamen verwenden. Geometrie-/Zeitfehler nicht durch ungeprüfte Interpolation oder erfundene Posen kaschieren.

[Zurück](../06_measure/TUTORIAL.md) · [Weiter](../08_lines/TUTORIAL.md) · [Index](../../TUTORIAL_INDEX.md)
