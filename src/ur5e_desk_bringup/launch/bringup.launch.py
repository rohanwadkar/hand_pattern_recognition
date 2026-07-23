import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    gazebo_pkg_share = get_package_share_directory('ur5e_desk_gazebo')
    moveit_pkg_share = get_package_share_directory('ur5e_desk_moveit_config')
    bringup_pkg_share = get_package_share_directory('ur5e_desk_bringup')

    rviz_config_file = os.path.join(bringup_pkg_share, 'rviz', 'ur5e_desk.rviz')

    # Gazebo Simulation
    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_pkg_share, 'launch', 'sim.launch.py')
        )
    )

    # MoveIt 2 Motion Planning
    moveit_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(moveit_pkg_share, 'launch', 'moveit.launch.py')
        )
    )

    # Gesture Recognition Node
    gesture_node = Node(
        package='gesture_recognition',
        executable='gesture_node',
        output='screen',
        parameters=[{'webcam_index': 0, 'debounce_frames': 15, 'confidence_threshold': 0.7}],
    )

    # RGB-D Object Detection Node
    object_detection_node = Node(
        package='ur5e_desk_perception',
        executable='object_detection_node',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    # Arm Motion Control Node
    arm_control_node = Node(
        package='ur5e_desk_control',
        executable='arm_control_node',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    # Task Manager Orchestrator Node
    task_manager_node = Node(
        package='ur5e_desk_control',
        executable='task_manager_node.py',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    # RViz 2 Dashboard Node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': True}],
    )

    return LaunchDescription([
        sim_launch,
        moveit_launch,
        gesture_node,
        object_detection_node,
        arm_control_node,
        task_manager_node,
        rviz_node,
    ])
