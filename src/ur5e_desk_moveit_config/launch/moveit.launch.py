import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    moveit_pkg_share = get_package_share_directory('ur5e_desk_moveit_config')
    desc_pkg_share = get_package_share_directory('ur5e_desk_description')

    # Robot Description
    xacro_file = os.path.join(desc_pkg_share, 'urdf', 'ur5e_desk.urdf.xacro')
    robot_description_content = Command([FindExecutable(name='xacro'), ' ', xacro_file])
    robot_description = {'robot_description': robot_description_content}

    # SRDF
    srdf_file = os.path.join(moveit_pkg_share, 'config', 'ur5e_desk.srdf')
    with open(srdf_file, 'r') as f:
        robot_description_semantic = {'robot_description_semantic': f.read()}

    # Kinematics
    kinematics_yaml = os.path.join(moveit_pkg_share, 'config', 'kinematics.yaml')

    # OMPL
    ompl_planning_yaml = os.path.join(moveit_pkg_share, 'config', 'ompl_planning.yaml')

    # Controllers
    moveit_controllers_yaml = os.path.join(moveit_pkg_share, 'config', 'moveit_controllers.yaml')

    # MoveGroup Node
    move_group_node = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[
            robot_description,
            robot_description_semantic,
            kinematics_yaml,
            ompl_planning_yaml,
            moveit_controllers_yaml,
            {'use_sim_time': True},
        ],
    )

    # Planning Scene Initializer Node
    planning_scene_initializer = Node(
        package='ur5e_desk_moveit_config',
        executable='planning_scene_initializer.py',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    return LaunchDescription([
        move_group_node,
        planning_scene_initializer,
    ])
