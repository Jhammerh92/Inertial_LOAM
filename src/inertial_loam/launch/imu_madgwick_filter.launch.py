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

    other_package_name='imu_filter_madgwick'
    config_dir = os.path.join(get_package_share_directory(package_name), 'config')

    madgwick_node = Node(
        package=other_package_name,
        name="imu_madgwick_filter",
        executable="imu_filter_madgwick_node",
        parameters=[os.path.join(config_dir, 'imu_filter_madgwick.yaml'),]
                                    # {"use_mag" : False,
                                    #  "gain": 0.3,
                                    #  "remove_gravity_vector": True,
                                    #  "constant_dt": 0.0 }],
        # arguments=['-p','use_mag:=false'],
        # remappings=[('/imu/data_raw','/imu/data_filter')],
        
    )



    ld.add_action(madgwick_node)

    return ld