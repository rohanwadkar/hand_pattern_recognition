import os
import yaml
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

    def load_yaml(filename):
        with open(os.path.join(moveit_pkg_share, 'config', filename), 'r') as stream:
            return yaml.safe_load(stream)

    # These files contain MoveIt dictionaries, not ROS parameter-file syntax.
    # Passing their paths to Node(parameters=...) makes rcl reject them.
    robot_description_kinematics = {
        'robot_description_kinematics': load_yaml('kinematics.yaml')
    }
    robot_description_planning = {
        'robot_description_planning': load_yaml('joint_limits.yaml')
    }
    ompl_yaml = load_yaml('ompl_planning.yaml')
    request_adapters = [
        'default_planning_request_adapters/ResolveConstraintFrames',
        'default_planning_request_adapters/ValidateWorkspaceBounds',
        'default_planning_request_adapters/CheckStartStateBounds',
        'default_planning_request_adapters/CheckStartStateCollision',
    ]
    # MoveIt reads the selected pipeline from the literal "ompl.*" parameter
    # namespace. Use flattened names so launch cannot reinterpret the mapping.
    planning_pipeline = {
        'planning_pipelines': ['ompl'],
        'default_planning_pipeline': 'ompl',
        'ompl.planning_plugins': ['ompl_interface/OMPLPlanner'],
        'ompl.request_adapters': request_adapters,
        'ompl.response_adapters': [
            'default_planning_response_adapters/AddTimeOptimalParameterization',
            'default_planning_response_adapters/ValidateSolution',
            'default_planning_response_adapters/DisplayMotionPath',
        ],
        'ompl.start_state_max_bounds_error': 0.1,
        'ompl.planner_configs': ompl_yaml['planner_configs'],
    }
    for group_name, group_config in ompl_yaml.items():
        if group_name == 'planner_configs':
            continue
        for key, value in group_config.items():
            planning_pipeline[f'ompl.{group_name}.{key}'] = value
    moveit_controllers = load_yaml('moveit_controllers.yaml')

    # MoveGroup Node
    move_group_node = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[
            robot_description,
            robot_description_semantic,
            robot_description_kinematics,
            robot_description_planning,
            planning_pipeline,
            moveit_controllers,
            {
                'use_sim_time': True,
                'publish_robot_description': True,
                'publish_robot_description_semantic': True,
            },
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
