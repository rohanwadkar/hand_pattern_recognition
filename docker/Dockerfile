FROM ros:jazzy-ros-base

ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=jazzy

# Install system dependencies, Gazebo Harmonic, MoveIt 2, OpenCV, and Build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
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
RUN pip install --no-cache-dir --break-system-packages \
    opencv-python \
    mediapipe \
    numpy \
    scipy \
    pyyaml

# Set up ROS 2 workspace environment
WORKDIR /ros2_ws

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
