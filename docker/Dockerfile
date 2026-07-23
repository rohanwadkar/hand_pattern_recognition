FROM osrf/ros:jazzy-desktop-full


ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=jazzy

# ROS binary packages are updated independently. Bump this value when rebuilding
# so Docker does not reuse stale apt metadata with newer, ABI-incompatible packages.
ARG ROS_APT_CACHE_BUST=2026-07-24-2

# Install system dependencies, Gazebo Harmonic, MoveIt 2, OpenCV, and Build tools
RUN echo "Refreshing ROS apt metadata: ${ROS_APT_CACHE_BUST}" \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get update \
    # The ROS base image and packages.ros.org can be from different syncs.
    # Upgrade the base as one unit before adding packages to avoid C++ ABI skew.
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    python3-pip \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool \
    ros-jazzy-desktop \
    gdb \
    ros-jazzy-ros-gz \
    ros-jazzy-ros-gz-bridge \
    ros-jazzy-ros-gz-sim \
    ros-jazzy-gz-ros2-control \
    ros-jazzy-ros2-control \
    ros-jazzy-ros2-controllers \
    ros-jazzy-joint-state-publisher \
    ros-jazzy-joint-state-publisher-gui \
    ros-jazzy-robot-state-publisher \
    ros-jazzy-xacro \
    ros-jazzy-moveit \
    ros-jazzy-moveit-ros-visualization \
    ros-jazzy-moveit-planners-ompl \
    ros-jazzy-ur-description \
    ros-jazzy-tf2-ros \
    ros-jazzy-tf2-geometry-msgs \
    ros-jazzy-cv-bridge \
    ros-jazzy-image-transport \
    ros-jazzy-sensor-msgs \
    ros-jazzy-std-msgs \
    ros-jazzy-geometry-msgs \
    libgl1-mesa-dri \
    libgl1 \
    libglx-mesa0 \
    v4l-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Python ML/Computer Vision libraries
# Keep the Debian/ROS-provided numpy (1.26.x): --ignore-installed avoids pip
# trying to uninstall the apt-managed numpy (which fails: no RECORD file), and
# pinning numpy<2 preserves ABI compatibility with ROS packages (cv_bridge, etc.)
RUN pip install --no-cache-dir --break-system-packages --ignore-installed \
    "numpy<2" \
    opencv-python \
    "mediapipe==0.10.21" \
    scipy \
    pyyaml

# Set up ROS 2 workspace environment
WORKDIR /ros2_ws

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
