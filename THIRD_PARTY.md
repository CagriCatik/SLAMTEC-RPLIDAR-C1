# Third-party components

Eigener Python-/C++-/Dokumentationscode: MIT, siehe LICENSE.

SLAMTEC rplidar_sdk: externe, gepinnte Abhängigkeit `99478e5fb90de3b4a6db0080acacd373f8b36869`. SDK-LICENSE und Bibliotheksheader enthalten BSD-2-Clause-Bedingungen; Demoanwendungen sind laut upstream README gesondert GPLv3. Unser Build verwendet nur sdk/, nicht app/-Demos. Keine Vendor-Demo wurde als eigene Bridge kopiert. Der Build kopiert die SDK-Lizenz zum verlinkten Binary; bei Weitergabe des Binaries diese Bedingungen mitführen. Quelle: https://github.com/Slamtec/rplidar_sdk

sllidar_ros2 und SLAM Toolbox werden als externe ROS-Pakete eingebunden, nicht vendort. Deren jeweilige Lizenz-/Distributionsbedingungen gelten separat. NumPy und Matplotlib behalten ihre eigenen Lizenzen. README-Badges sind entfernte Statusbilder; keine Coverage-/Hardwarezertifizierung wird erfunden.
