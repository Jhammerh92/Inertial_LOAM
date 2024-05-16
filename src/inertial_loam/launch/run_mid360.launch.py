from launch import LaunchDescription
from launch_ros.actions import Node, SetRemap
from launch.actions import IncludeLaunchDescription, ExecuteProcess, GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
# from math import pi, radians
import os.path

from datetime import datetime

## TODO create a live sensor launch file, and use that in record_launch

def generate_launch_description():
    ld = LaunchDescription()

    lidar_driver_node= IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('livox_ros_driver2'), 'launch_ROS2', 'ros_MID360_launch.py')]),
    )

    # to follow in rviz
    transform_node_livox = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments = [ '0', '0', '0', '0', '0', '0' , 'odom', 'livox_frame']
    )
 

    ld.add_action(lidar_driver_node)
    ld.add_action(transform_node_livox)

    return ld