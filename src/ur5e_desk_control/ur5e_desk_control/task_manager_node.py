#!/usr/bin/env python3
import time
import threading
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Pose

from ur5e_desk_interfaces.srv import DetectObjects

class TaskManagerNode(Node):
    def __init__(self):
        super().__init__('task_manager_node')

        self.state = "IDLE"  # IDLE, PERCEIVING, EXECUTING, ERROR

        # Subscription to gesture commands
        self.create_subscription(String, '/gesture_command', self.gesture_callback, 10)

        # Service Client to object perception
        self.detect_cli = self.create_client(DetectObjects, '/detect_objects')

        # Bin Target Poses
        self.bins = {
            'red': self.make_pose(-0.35, 0.45, 0.85),
            'blue': self.make_pose(0.0, 0.45, 0.85),
            'green': self.make_pose(0.35, 0.45, 0.85),
            'primary': self.make_pose(-0.35, 0.45, 0.85),
        }

        self.get_logger().info("Task Manager Orchestrator Node started. Waiting for gesture commands...")

    def make_pose(self, x, y, z):
        p = Pose()
        p.position.x = x
        p.position.y = y
        p.position.z = z
        p.orientation.w = 1.0
        return p

    def gesture_callback(self, msg):
        cmd = msg.data
        if self.state != "IDLE":
            self.get_logger().warn(f"System is busy ({self.state}). Ignoring command '{cmd}'.")
            return

        tasks = {
            "pick_and_place": self.execute_task_1,
            "sort_by_color": self.execute_task_2,
            "stack_objects": self.execute_task_3,
        }
        task = tasks.get(cmd)
        if task is None:
            self.get_logger().error(f"Unknown gesture command '{cmd}'.")
            return

        # Service waits and the simulated execution sleeps must not block the
        # executor thread that delivers service responses and new ROS events.
        self.state = "PERCEIVING"
        self.get_logger().info(f"Received gesture command: '{cmd}'. Executing workflow...")
        threading.Thread(target=task, daemon=True).start()

    def call_detect_objects(self, color_filter="all"):
        if not self.detect_cli.wait_for_service(timeout_sec=3.0):
            self.get_logger().error("Vision perception service /detect_objects not available.")
            return []

        req = DetectObjects.Request()
        req.filter_color = color_filter
        future = self.detect_cli.call_async(req)
        completed = threading.Event()
        future.add_done_callback(lambda _: completed.set())
        if not completed.wait(timeout=5.0):
            self.get_logger().error("Vision perception service timed out.")
            return []
        res = future.result()
        if res and res.success:
            return res.objects
        return []

    def execute_task_1(self):
        """Gesture 1: Pick & Place closest object into primary bin."""
        self.state = "PERCEIVING"
        objects = self.call_detect_objects("all")
        if not objects:
            self.get_logger().warn("Task 1: No objects detected on desk.")
            self.state = "IDLE"
            return

        target_obj = objects[0]  # Closest to center
        self.get_logger().info(f"Task 1: Selected closest object '{target_obj.id}' at ({target_obj.pose.position.x:.2f}, {target_obj.pose.position.y:.2f}).")

        self.state = "EXECUTING"
        # Simulated execution sequence call
        time.sleep(1.0)
        self.get_logger().info(f"Task 1: Picked object '{target_obj.id}' and placed into Primary Bin.")
        self.get_logger().info("Task 1 Completed. UR5e returned to Home pose.")
        self.state = "IDLE"

    def execute_task_2(self):
        """Gesture 2: Sort all red, blue, and green objects into respective color bins."""
        self.state = "PERCEIVING"
        objects = self.call_detect_objects("all")
        if not objects:
            self.get_logger().warn("Task 2: No objects detected on desk.")
            self.state = "IDLE"
            return

        self.state = "EXECUTING"
        for obj in objects:
            dest_bin = self.bins.get(obj.color, self.bins['primary'])
            self.get_logger().info(f"Task 2: Sorting '{obj.color}' object '{obj.id}' to {obj.color.capitalize()} Bin...")
            time.sleep(1.0)

        self.get_logger().info("Task 2 Completed: All detected objects sorted. UR5e returned to Home pose.")
        self.state = "IDLE"

    def execute_task_3(self):
        """Gesture 3: Stack up to 3 objects on a base object."""
        self.state = "PERCEIVING"
        objects = self.call_detect_objects("all")
        if len(objects) < 2:
            self.get_logger().warn(f"Task 3: Stack objects requires at least 2 objects, but found {len(objects)}. Stopping safely.")
            self.state = "IDLE"
            return

        self.state = "EXECUTING"
        base_obj = objects[0]
        self.get_logger().info(f"Task 3: Selected base object '{base_obj.id}' at ({base_obj.pose.position.x:.2f}, {base_obj.pose.position.y:.2f}).")

        stack_count = min(len(objects), 3)
        cube_height = 0.04

        for i in range(1, stack_count):
            curr_obj = objects[i]
            target_z = base_obj.pose.position.z + (i * cube_height)
            self.get_logger().info(f"Task 3: Stacking object '{curr_obj.id}' on base object at Z={target_z:.2f}m...")
            time.sleep(1.0)

        self.get_logger().info(f"Task 3 Completed: Stacked {stack_count} objects. UR5e returned to Home pose.")
        self.state = "IDLE"

def main(args=None):
    rclpy.init(args=args)
    node = TaskManagerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
