# 12 — Landmarkenkarte

## Ziel und Code

Linien-/Ecken-/Cluster-Hypothesen mit Sitzungs-ID, Pose und Scanbelegen. Variierende Kontur/Symmetrie/Drift können Identität verfälschen.

Dieser Ordner enthält die Anleitung. Gemeinsamer ausführbarer Code: **landmarks.py**, keine duplizierten Kameras-/Scannerskripte.

## Ausführen

Alle Befehle im Repository-Hauptverzeichnis, Pythonumgebung aktiviert. Demo benötigt NumPy, Viewer zusätzlich Matplotlib; Hardware benötigt Bridge/Adapter, ROS seine Systempakete.

```bash
c1-lab map --scans 5 --output recordings/tutorial-12
c1-lab landmarks --input recordings/tutorial-12/landmarks.json --confirmed
```

Erwartung: Karte mit Landmarken-JSON/CSV und Beobachtungsjournal; Abfrage der mehrfach zugeordneten Merkmale. Details zu den Feldern und Formaten: [Anwendungsreferenz](../../docs/applications.md).

## Experiment und Grenzen

Vergleiche Quellenbelege der gleichen Landmarke über mehrere Scans. Achte auf Sichtbarkeitsänderung und mögliche ID-Aufteilung. Ein erfolgreicher Programmlauf beweist keine Hardwaregenauigkeit.

Bei fehlenden Paketen/Portzugriff der [Einrichtung](../../docs/setup.md) folgen; neue Ausgabenamen verwenden. Geometrie-/Zeitfehler nicht durch ungeprüfte Interpolation oder erfundene Posen kaschieren.

[Zurück](../11_mapping/TUTORIAL.md) · [Weiter](../13_ros2/TUTORIAL.md) · [Index](../../TUTORIAL_INDEX.md)
