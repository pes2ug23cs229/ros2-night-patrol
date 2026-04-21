import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg = get_package_share_directory('night_patrol_robot')

    urdf_file = os.path.join(pkg, 'urdf', 'patrol_robot.urdf.xacro')
    nav2_param = os.path.join(pkg, 'config', 'nav2_params.yaml')
    navigation_launch = os.path.join(pkg, 'launch', 'navigation_launch.py')

    robot_description = ParameterValue(
        Command(['xacro ', urdf_file]),
        value_type=str
    )

    # -------------------------
    # Robot State Publisher
    # -------------------------
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True
        }],
        output='screen',
    )

    # -------------------------
    # 🔥 FIXED SPAWN (CENTER)
    # -------------------------
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'patrol_robot',
            '-topic', 'robot_description',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.3'
        ],
        output='screen',
    )

    # -------------------------
    # 🔥 FIXED BRIDGE
    # -------------------------

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
            '/camera/image_raw@sensor_msgs/msg/Image@gz.msgs.Image',
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            '/clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock',
            '/joint_states@sensor_msgs/msg/JointState@gz.msgs.Model',
            '/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
            '--ros-args', '-p', 'lazy:=false',
        ],
        output='screen',
    )
    

    # -------------------------
    # NAV2
    # -------------------------
    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(navigation_launch),
        launch_arguments={
            'use_sim_time': 'true',
            'params_file': nav2_param,
        }.items(),
    )

    # -------------------------
    # PATROL NODE
    # -------------------------
    patrol_node = Node(
        package='night_patrol_robot',
        executable='patrol_node',
        name='patrol_node',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    return LaunchDescription([
        robot_state_publisher,
        spawn_robot,
        patrol_node,
    ])
