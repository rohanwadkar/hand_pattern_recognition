import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    ExecuteProcess,
    IncludeLaunchDescription,
    RegisterEventHandler,
    TimerAction,
)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    pkg_share = get_package_share_directory('ur5e_desk_gazebo')
    desc_pkg_share = get_package_share_directory('ur5e_desk_description')
    world_path = os.path.join(pkg_share, 'worlds', 'desk_world.sdf')

    # Robot Description xacro command
    xacro_file = os.path.join(desc_pkg_share, 'urdf', 'ur5e_desk.urdf.xacro')
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name='xacro')]),
            ' ',
            xacro_file,
        ]
    )
    robot_description = {'robot_description': robot_description_content}

    # Gazebo Sim Launch
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'])
        ),
        # Run the simulator server only. RViz is the visualization dashboard;
        # starting a second Ogre GUI in the same software-rendered container
        # causes competing GLX contexts and prevents the world from loading.
        launch_arguments={'gz_args': f'-r -s {world_path}'}.items(),
    )

    # Attach the Gazebo client only after the server has created the world.
    # This avoids the gz launcher waiting forever on GUI GL initialization.
    gz_client = ExecuteProcess(
        cmd=['gz', 'sim', '-g', '--force-version', '8'],
        output='screen',
        additional_env={
            'QT_XCB_GL_INTEGRATION': 'xcb_glx',
        },
    )

    # Robot State Publisher Node
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='both',
        parameters=[robot_description, {'use_sim_time': True}],
    )

    # Spawn Robot Entity in Gazebo
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'ur5e_desk',
            '-string', robot_description_content,
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.0',
        ],
        output='screen',
    )

    # ROS-Gazebo Bridge for Clock and Camera Topics
    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/world/desk_world/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera/depth/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            '/camera/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
        ],
        remappings=[
            ('/world/desk_world/clock', '/clock'),
        ],
        output='screen',
    )

    # Controller Spawners
    joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster',
            '--controller-manager', '/controller_manager',
            '--controller-manager-timeout', '60',
        ],
        output='screen',
    )

    ur_manipulator_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'ur_manipulator_controller',
            '--controller-manager', '/controller_manager',
            '--controller-manager-timeout', '60',
        ],
        output='screen',
    )

    gripper_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'gripper_controller',
            '--controller-manager', '/controller_manager',
            '--controller-manager-timeout', '60',
        ],
        output='screen',
    )

    return LaunchDescription([
        gz_sim,
        TimerAction(period=6.0, actions=[gz_client]),
        robot_state_publisher,
        spawn_robot,
        ros_gz_bridge,
        # Do not race controller spawners against insertion of the robot and its
        # gz_ros2_control controller manager.
        RegisterEventHandler(
            OnProcessExit(
                target_action=spawn_robot,
                on_exit=[
                    joint_state_broadcaster,
                    ur_manipulator_spawner,
                    gripper_spawner,
                ],
            )
        ),
    ])
