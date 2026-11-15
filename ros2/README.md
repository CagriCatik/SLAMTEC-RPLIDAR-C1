# ROS 2 / RViz / SLAM Toolbox

Zielumgebung ist Ubuntu 24.04 / Jazzy. Der geprüfte upstream README führt nicht ausdrücklich alle Jazzy-Kombinationen auf; installierten Treiber und Buildkompatibilität separat prüfen. Hier kein ROS-Lauf, nur Python-Syntax und API-Abgleich mit offiziellem C1-Launch.

Nach Installation/Build von sllidar_ros2 und Sourcen deiner Umgebung, aus dem Repository-Hauptverzeichnis:

```bash
source /opt/ros/jazzy/setup.bash
ros2 launch "$PWD/ros2/c1.launch.py" serial_port:=/dev/ttyUSB0
ros2 topic echo /scan --once
ros2 topic hz /scan
rviz2
```

RViz Fixed Frame zunächst `laser`, LaserScan `/scan` hinzufügen; Topic-/QoS-Werte prüfen. Der Launch verwendet offiziellen C1-Einstieg, 460800 Baud, inverted=false und angle_compensate=true. Kompensiertes LaserScan ist ein abgeleitetes Winkelraster. Die SDK-Bridge ist der Pfad für unveränderte HQ-Punkte. Treiberzeitfelder/Inf-Werte nicht unbesehen als beweiskräftige Einzelpunktzeiten/Freiraum verwenden.

```bash
ros2 bag record -o recordings/ros-001 /scan /tf /tf_static /odom
# In eigenem Prozess, wenn gültige Odometrie und Roboter-TFs vorliegen:
ros2 launch "$PWD/ros2/slam.launch.py"
```

SLAM Toolbox braucht die echte Kette `odom -> base_link -> laser` mit korrekter Montage und zeitlich passenden Transformationen. Keine erfundene Identitäts-Odometrie publizieren. Ein handbewegter Scanner ohne Odometrie ist damit noch kein vollständig eingerichteter ROS-SLAM-Aufbau; die standalone NumPy-Kette kann unabhängig lokal schätzen. ROS und Standalone-Posen/Karten werden nicht automatisch gekoppelt.

SLAM-Launch übernimmt upstream online_async_launch.py und eigene Parameterdatei. `use_sim_time:=true` nur bei passender Sim-/Bag-Uhr. ROS-Loop-Closure, Lifecycles und Datenbank-/Kartenexport müssen mit der installierten Version geprüft werden. Keine Roboterbewegungsbefehle oder Nav2-Controller enthalten. Vorher Standalone-Bridge und andere Portnutzer schließen.
