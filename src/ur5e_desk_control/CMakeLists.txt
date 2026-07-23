cmake_minimum_required(VERSION 3.8)
project(ur5e_desk_control)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclcpp REQUIRED)
find_package(moveit_ros_planning_interface REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(ur5e_desk_interfaces REQUIRED)

# Build C++ Arm Control Node
add_executable(arm_control_node src/arm_control_node.cpp)
ament_target_dependencies(arm_control_node
  rclcpp
  moveit_ros_planning_interface
  geometry_msgs
  std_msgs
  ur5e_desk_interfaces
)

install(TARGETS
  arm_control_node
  DESTINATION lib/${PROJECT_NAME}
)

# Install Python scripts
ament_python_install_package(ur5e_desk_control)

install(PROGRAMS
  ur5e_desk_control/task_manager_node.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
