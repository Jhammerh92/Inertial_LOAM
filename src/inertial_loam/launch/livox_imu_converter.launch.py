import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import xacro
package_name = 'inertial_loam'


def generate_launch_description():

    # Specify the name of the package and path to xacro file within the package
    config_dir = os.path.join(get_package_share_directory(package_name), 'config')


    imu_convert_node = Node(
        package=package_name,
        executable="livox_imu_converter",
        parameters=[os.path.join(config_dir, 'livox_imu_converter.yaml')],
    )
    


    # Run the node
    return LaunchDescription([
        imu_convert_node,
        # transform_node_map_odom,
        # node_joint_state_publisher_gui
    ])