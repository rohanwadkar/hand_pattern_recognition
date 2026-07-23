#!/bin/bash
set -e

# Source ROS 2 environment
source "/opt/ros/$ROS_DISTRO/setup.bash"

# Source workspace if built
if [ -f "/ros2_ws/install/setup.bash" ]; then
    source "/ros2_ws/install/setup.bash"
fi

exec "$@"
