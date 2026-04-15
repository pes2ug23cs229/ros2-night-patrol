import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, TextSubstitution

def generate_launch_description():

    pkg_night_patrol = get_package_share_directory('night_patrol_world')
    pkg_ros_gz_sim   = get_package_share_directory('ros_gz_sim')

    # Make sure Gazebo can find your models folder
    models_path = os.path.join(pkg_night_patrol, 'models')
    if 'GZ_SIM_RESOURCE_PATH' in os.environ:
        os.environ['GZ_SIM_RESOURCE_PATH'] += os.pathsep + models_path
    else:
        os.environ['GZ_SIM_RESOURCE_PATH'] = models_path

    world_file = os.path.join(pkg_night_patrol, 'worlds', 'city_world.sdf')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': world_file + ' -r -v 1',  # -r = run immediately
            'on_exit_shutdown': 'true'
        }.items()
    )

    return LaunchDescription([gazebo])

