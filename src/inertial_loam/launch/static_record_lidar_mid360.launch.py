from launch import LaunchDescription
from launch_ros.actions import Node, SetRemap
from launch.actions import IncludeLaunchDescription, ExecuteProcess, GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
# from math import pi, radians
import os.path

package_name = 'inertial_loam'



def generate_launch_description():
    ld = LaunchDescription()

    
    config_dir = os.path.join(get_package_share_directory(package_name), 'config')


    # lidar_driver_node= IncludeLaunchDescription(
    #             PythonLaunchDescriptionSource([os.path.join(
    #                 get_package_share_directory('livox_ros_driver2'), 'launch_ROS2', 'ros_HAP_launch.py')]),
    # )

     # rewrite to use the run_HAP launcher
    lidar_driver_launch= IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name), 'launch', 'run_mid360.launch.py')]),
    )

    static_record_node = Node(
        package=package_name,
        name="static_recorder",
        executable="static_recorder",
        parameters=[os.path.join(config_dir, 'static_recorder.yaml')],
        # arguments=[]
    )


    ld.add_action(lidar_driver_launch)
    ld.add_action(static_record_node)

    return ld