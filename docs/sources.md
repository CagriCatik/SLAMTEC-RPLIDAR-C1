# Quellen, Modellrevision und verifizierter Stand

Quellenprüfung: 15.11.2026. Geräteziel ist C1M1-R2. Aktuelle C1-Unterlagen dürfen nicht ohne Revisionsabgleich als vollständige R2-Spezifikation ausgegeben werden.

| Quelle | Verwendung / Prüfung |
|---|---|
| [C1 Spezifikation](https://www.slamtec.com/en/c1/spec) | Offizielle aktuelle C1-Eckdaten; öffentlich gelesen |
| [Herstellersupport](https://www.slamtec.com/en/support) | Datenblatt, Handbuch und Protokoll |
| [R2-Datenblatt v1.0](https://wiki.slamtec.com/download/attachments/83066883/SLAMTEC_rplidar_datasheet_C1_v1.0_en.pdf?api=v2&modificationDate=1700531479533&version=1) | Herstellerindex nennt C1M1-R2; vollständiger PDF-Abruf hier wegen Timeout nicht gelungen |
| [C1M1-Datenblatt v1.1](https://bucket-download.slamtec.com/2d4664be9f9f5c748f3b608f2cf1862962b168eb/SLAMTEC_rplidar_datasheet_C1_v1.1_en.pdf) | Index nennt C1M1 ohne R2; Abruf hier 403, Revisionsgleichheit offen |
| [Offizielles SDK](https://github.com/Slamtec/rplidar_sdk) | Ausgecheckt/gebaut: `99478e5fb90de3b4a6db0080acacd373f8b36869` |
| [Offizieller ROS-2-Treiber](https://github.com/Slamtec/sllidar_ros2) | Code geprüft: `34300099fadfc772965962dec837bf436706188f`; kein ROS-Lauf |
| [SLAM Toolbox](https://github.com/SteveMacenski/slam_toolbox) | Launch-/Parameter-API gegen ros2-Branch gelesen; nicht gebaut/ausgeführt |

Aktuelle Herstellerwebwerte: weiße Ziele 0,05–12 m bei 70 % Reflexion; schwarze Ziele 0,05–6 m bei 10 %; 5 kHz Sampling; 8–12 Hz Rotation, typisch 10 Hz; typische Winkelauflösung 0,72°; TTL-UART 460800 Baud; Genauigkeitsangabe ±30 mm. Diese Werte sind keine hier gemessenen Ergebnisse. Bedingungen/Revisionen müssen für einen Konformitätsvergleich vollständig aus dem passenden Datenblatt verifiziert werden. Rotationsrate und Messpunktrate sind unterschiedliche Größen. Herstellerangabe Scan-Pitch 0–1,5° bedeutet keine verfügbare allgemeine 3D-/Höhenmessung.

Ungeklärt bleiben der vollständige R2/v1.1-Revisionsvergleich, konkrete elektrische/Stecker-/Montage-/Umweltbedingungen sowie zusätzliche herstellerspezifische Qualitäts-/Reflektivitäts-/2.5D-Angaben. Die Bridge exportiert nur tatsächlich verfügbare HQ-Felder; sie interpretiert keine unbestätigten Zusatzkanäle.

SDK-Header geprüft: `createSerialPortChannel`, `getDeviceInfo`, `getHealth`, `getAllSupportedScanModes`, `startScan/startScanExpress`, `grabScanDataHq`, `setMotorSpeed`, `stop`, `disconnect`. Hardware-Abtastzeiten werden nicht aus Host-Empfangsdauer erfunden. Die ROS-Achskonvention wird im nicht invertierten Treiber mit `pi-native_angle` umgesetzt; die Bridge speichert zusätzlich die unveränderten Q14-Werte.
