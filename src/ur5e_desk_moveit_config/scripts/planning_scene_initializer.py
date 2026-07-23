#!/usr/bin/env python3
import time
import rclpy
from rclpy.node import Node
from moveit_msgs.msg import PlanningScene, CollisionObject
from shape_msgs.msg import SolidPrimitive
from geometry_msgs.msg import Pose

class PlanningSceneInitializer(Node):
    def __init__(self):
        super().__init__('planning_scene_initializer')
        self.publisher = self.create_publisher(PlanningScene, '/planning_scene', 10)
        self.timer = self.create_timer(2.0, self.publish_scene)
        self.get_logger().info('Planning Scene Initializer Node Started.')

    def publish_scene(self):
        scene = PlanningScene()
        scene.is_diff = True

        # Desk Collision Object
        desk = CollisionObject()
        desk.header.frame_id = 'world'
        desk.id = 'desk'

        box = SolidPrimitive()
        box.type = SolidPrimitive.BOX
        box.dimensions = [1.2, 0.8, 0.75]

        pose = Pose()
        pose.position.x = 0.0
        pose.position.y = 0.25
        pose.position.z = 0.375
        pose.orientation.w = 1.0

        desk.primitives.append(box)
        desk.primitive_poses.append(pose)
        desk.operation = CollisionObject.ADD

        scene.world.collision_objects.append(desk)

        # Red Bin Collision Object
        red_bin = CollisionObject()
        red_bin.header.frame_id = 'world'
        red_bin.id = 'red_bin'
        bin_box = SolidPrimitive()
        bin_box.type = SolidPrimitive.BOX
        bin_box.dimensions = [0.22, 0.22, 0.1]
        bin_pose = Pose()
        bin_pose.position.x = -0.35
        bin_pose.position.y = 0.45
        bin_pose.position.z = 0.8
        bin_pose.orientation.w = 1.0
        red_bin.primitives.append(bin_box)
        red_bin.primitive_poses.append(bin_pose)
        red_bin.operation = CollisionObject.ADD
        scene.world.collision_objects.append(red_bin)

        # Blue Bin Collision Object
        blue_bin = CollisionObject()
        blue_bin.header.frame_id = 'world'
        blue_bin.id = 'blue_bin'
        blue_pose = Pose()
        blue_pose.position.x = 0.0
        blue_pose.position.y = 0.45
        blue_pose.position.z = 0.8
        blue_pose.orientation.w = 1.0
        blue_bin.primitives.append(bin_box)
        blue_bin.primitive_poses.append(blue_pose)
        blue_bin.operation = CollisionObject.ADD
        scene.world.collision_objects.append(blue_bin)

        # Green Bin Collision Object
        green_bin = CollisionObject()
        green_bin.header.frame_id = 'world'
        green_bin.id = 'green_bin'
        green_pose = Pose()
        green_pose.position.x = 0.35
        green_pose.position.y = 0.45
        green_pose.position.z = 0.8
        green_pose.orientation.w = 1.0
        green_bin.primitives.append(bin_box)
        green_bin.primitive_poses.append(green_pose)
        green_bin.operation = CollisionObject.ADD
        scene.world.collision_objects.append(green_bin)

        self.publisher.publish(scene)
        self.get_logger().info('Published MoveIt planning scene collision objects.')

def main(args=None):
    rclpy.init(args=args)
    node = PlanningSceneInitializer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
