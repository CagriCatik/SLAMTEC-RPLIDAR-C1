"""SLAM Toolbox entry; requires an external, valid odom->base_link->laser TF chain."""
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    upstream = Path(get_package_share_directory("slam_toolbox"))/"launch"/"online_async_launch.py"
    return LaunchDescription([
        DeclareLaunchArgument("use_sim_time", default_value="false"),
        DeclareLaunchArgument("slam_params_file", default_value=str(Path(__file__).with_name("slam.yaml"))),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(str(upstream)), launch_arguments={
            "use_sim_time": LaunchConfiguration("use_sim_time"), "slam_params_file": LaunchConfiguration("slam_params_file"),
        }.items())])
