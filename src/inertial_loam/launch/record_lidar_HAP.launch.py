from launch import LaunchDescription
from launch_ros.actions import Node, SetRemap
from launch.actions import IncludeLaunchDescription, ExecuteProcess, GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
# from math import pi, radians
import os.path

from datetime import datetime

package_name = 'inertial_loam'


## TODO create a live sensor launch file, and use that in record_launch

def generate_launch_description():
    ld = LaunchDescription()

    

    recorded_topics = ["/livox/lidar","/livox/imu", "/imu/data_raw", "/imu/mag", "/imu/time_ref"]

    now = datetime.now()
    # dt_string = now.strftime("%d%m%Y_%H%M%S") --> format leads to bad sorting of files in terminal
    dt_string = now.strftime("%Y%m%d_%H%M%S")

    # config_dir = os.path.join(get_package_share_directory(package_name), 'config')
    recordings_dir = r'/home/slamnuc/bagfiles'
    recording_name = 'lidar_HAP_' + dt_string

    print(f"Recording to folder: {recording_name}")

    # rewrite to use the run_HAP launcher
    lidar_driver_launch= IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    # get_package_share_directory('livox_ros_driver2'), 'launch_ROS2', 'ros_HAP_launch.py')]),
                    get_package_share_directory(package_name), 'launch', 'run_HAP.launch.py')]),
    )

    # xsens_launch = GroupAction(
    #     actions=[
    #         SetRemap(src="/imu/data", dst="/imu/data_raw"), # remap the out to something used by filter

    #         IncludeLaunchDescription( # IMU driver launch
    #                     PythonLaunchDescriptionSource([os.path.join(
    #                         get_package_share_directory('bluespace_ai_xsens_mti_driver'), 'launch', 'xsens_mti_node.launch.py')]),
    #         )
    #     ]
    # )

    xsens_launch= IncludeLaunchDescription(
            PythonLaunchDescriptionSource([os.path.join(
                get_package_share_directory(package_name), 'launch', 'run_xsens.launch.py')]),
    )

    # lidar_group_action_launch = GroupAction(
    #     actions=[
    #         SetRemap(src="/livox/imu", dst="/imu/data_HAP"), # ramap the out to something used by filter, remember to do this with RT imeplementation!
    #         lidar_driver_node
    #     ]
    # )
    # imu_launch = GroupAction(
    #     actions=[
    #         SetRemap(src="/imu/data", dst="/imu/data_raw"), # ramap the out to something used by filter, remember to do this with RT imeplementation!

    #         IncludeLaunchDescription( # IMU driver launch
    #                     PythonLaunchDescriptionSource([os.path.join(
    #                         get_package_share_directory('bluespace_ai_xsens_mti_driver'), 'launch', 'xsens_mti_node.launch.py')]),
    #         ),

    #         # lidar_driver_node = IncludeLaunchDescription(
    #         #     launch_description_source='/home/slamnuc/ws_livox/src/livox_ros2_driver/launch/livox_lidar_launch.py',
    #         #     # add launch arguments
    #         # )
    #     ]
    # )
    
    bag_node = ExecuteProcess(
            cmd=['ros2', 'bag', 'record'] +  recorded_topics + [ '-o', os.path.join(recordings_dir, recording_name)],
            output='screen'
    )
    
    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'false'}.items()
    )

    # to follow in rviz
    transform_node_livox = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments = [ '0', '0', '0', '0', '0', '0' , 'odom', 'livox_frame']
    
    )
 
    

    # ld.add_action(lidar_driver_node)
    ld.add_action(lidar_driver_launch)
    ld.add_action(xsens_launch)
    ld.add_action(transform_node_livox)
    ld.add_action(bag_node)

    return ld