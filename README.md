# Gesture-Controlled UR5e Robot Arm with Vision-Based Task Execution

A fully simulated robotic manipulation system developed with **ROS 2 (Jazzy)**, **Gazebo Harmonic**, **MoveIt 2**, **ros2_control**, **OpenCV**, and **MediaPipe**, running entirely inside a containerized **Docker** environment.

A human user performs hand gestures in front of a host computer webcam. The gestures are detected in real-time, filtered via debouncing and cooldown state logic, and published as task commands. A simulated UR5e 6-DOF robot arm equipped with a parallel-jaw gripper uses its overhead RGB-D camera to perceive, segment, and manipulate objects on a desk (Pick and Place, Color Sorting, and Object Stacking).

---

## 🌟 Key Features

* **Real-Time Webcam Hand Gesture Recognition**:
  * Powered by MediaPipe Hands & OpenCV.
  * Debouncing engine requiring $N$ consecutive matching frames before triggering.
  * Edge-trigger cooldown logic preventing continuous unintended execution.
* **3D Perception & RGB-D Object Detection**:
  * HSV color space segmentation (Red, Blue, Green objects).
  * Depth map projection ($2\text{D} \rightarrow 3\text{D}$ camera optical frame).
  * TF2 coordinate transformation to `base_link` robot frame.
  * Custom ROS 2 Service interface `/detect_objects`.
* **Collision-Aware Motion Planning**:
  * MoveIt 2 OMPL planning pipeline for UR5e 6-DOF arm.
  * Dynamic environment collision monitoring (table and bin obstacle injection).
* **Gazebo Harmonic Physics Simulation**:
  * Gazebo Harmonic environment (`desk_world.sdf`) featuring table, destination bins, and physical pickable cubes.
  * Hardware control via `gz_ros2_control` and `joint_trajectory_controller`.
* **Full Containerization**:
  * Portable Docker setup with GUI forwarding (X11) and host webcam device (`/dev/video0`) passthrough.

---

## 🖐️ Gesture-to-Task Mapping

| Gesture | Finger Count | Task Command | Description |
| :--- | :---: | :--- | :--- |
| **Gesture 1** | **1 Finger** (Index) | `pick_and_place` | Detects all objects on the desk, selects the object closest to the camera center, picks it, and places it into the primary bin. |
| **Gesture 2** | **2 Fingers** (Index + Middle) | `sort_by_color` | Classifies objects by color (Red, Blue, Green) and picks/places each object into its corresponding color-coded destination bin. |
| **Gesture 3** | **3 Fingers** (Index + Middle + Ring) | `stack_objects` | Identifies at least 2 stackable cubes, selects a base object, and stacks up to 3 cubes vertically on top of each other. |

---

## 🏗️ ROS 2 Package Architecture

```text
hand_pattern_recognition/
├── docker/
│   ├── Dockerfile             # ROS 2 Jazzy, Gazebo Harmonic, MoveIt 2 container
│   └── entrypoint.sh          # Container environment initialization
├── docker-compose.yml         # Container orchestration with GUI & Video passthrough
├── src/
│   ├── gesture_recognition/     # MediaPipe webcam gesture recognition node
│   ├── ur5e_desk_interfaces/   # Custom ROS 2 msg (DetectedObject) and srv (DetectObjects)
│   ├── ur5e_desk_description/  # URDF/Xacro for UR5e, gripper, camera & ros2_control
│   ├── ur5e_desk_gazebo/       # Gazebo Harmonic world (desk_world.sdf) & simulation spawner
│   ├── ur5e_desk_moveit_config/# MoveIt 2 SRDF, controllers, and planning scene initializer
│   ├── ur5e_desk_perception/   # RGB-D OpenCV 3D object detection & TF transform node
│   ├── ur5e_desk_control/      # C++ MoveIt 2 trajectory executor & Task Manager state machine
│   └── ur5e_desk_bringup/      # Master bringup launch file and RViz 2 dashboard
└── README.md
```

---

## 🚀 Quick Start Guide

### Prerequisites

* Linux OS (Ubuntu 22.04 / 24.04 recommended)
* Docker & Docker Compose installed
* Host webcam connected at `/dev/video0` (or update `docker-compose.yml`)
* X11 / Wayland display server for GUI visualization

### 1. Clone the Repository

```bash
git clone git@github.com:rohanwadkar/hand_pattern_recognition.git
cd hand_pattern_recognition
```

### 2. Build the Docker Image

Allow X11 forwarding on your host and build the container:

```bash
xhost +local:root
docker compose build
```

### 3. Launch the System

Run the Docker container and launch the complete ROS 2 bringup pipeline:

```bash
docker compose up -d
docker exec -it ros2_ur5e_container bash -c "colcon build && source install/setup.bash && ros2 launch ur5e_desk_bringup bringup.launch.py"
```

This master launch command brings up:
1. **Gazebo Harmonic**: Simulation world with UR5e robot arm, desk, and colored cubes.
2. **MoveIt 2**: `move_group` motion planning & collision scene initializer.
3. **Vision Perception**: `/detect_objects` RGB-D 3D pose estimation server.
4. **Gesture Recognition**: Webcam feed window displaying finger count, debouncing progress, and active state.
5. **Task Manager**: High-level task execution state machine.
6. **RViz 2**: Complete 3D robot, point cloud, and TF visualization dashboard.

---

## 📜 License

Distributed under the Apache 2.0 License.
