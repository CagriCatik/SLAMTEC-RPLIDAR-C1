"""Use the official C1 driver; its compensated LaserScan is a derived angular grid."""
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    upstream = Path(get_package_share_directory("sllidar_ros2"))/"launch"/"sllidar_c1_launch.py"
    return LaunchDescription([
        DeclareLaunchArgument("serial_port", default_value="/dev/ttyUSB0"),
        DeclareLaunchArgument("frame_id", default_value="laser"),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(str(upstream)), launch_arguments={
            "serial_port": LaunchConfiguration("serial_port"), "serial_baudrate": "460800",
            "frame_id": LaunchConfiguration("frame_id"), "inverted": "false", "angle_compensate": "true",
        }.items())])
