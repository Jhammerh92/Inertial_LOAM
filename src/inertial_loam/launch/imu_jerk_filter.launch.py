from launch import LaunchDescription
from launch_ros.actions import Node
# from launch.actions import IncludeLaunchDescription
from ament_index_python.packages import get_package_share_directory
# from launch.launch_description_sources import PythonLaunchDescriptionSource
# from math import pi, radians
import os.path
package_name = 'inertial_loam'


def generate_launch_description():
    ld = LaunchDescription()

    config_dir = os.path.join(get_package_share_directory(package_name), 'config')

    ekf_node = Node(
        package=package_name,
        name="imu_jerk_filter",
        executable="imu_filter",
        parameters=[os.path.join(config_dir, 'imu_filter.yaml')],
        # arguments=[]
    )



    ld.add_action(ekf_node)

    return ld