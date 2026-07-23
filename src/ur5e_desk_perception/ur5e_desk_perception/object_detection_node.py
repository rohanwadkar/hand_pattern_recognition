#!/usr/bin/env python3
import math
import numpy as np
import cv2

import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import PoseStamped
from tf2_ros import Buffer, TransformListener
import tf2_geometry_msgs

from ur5e_desk_interfaces.msg import DetectedObject
from ur5e_desk_interfaces.srv import DetectObjects

class ObjectDetectionNode(Node):
    def __init__(self):
        super().__init__('object_detection_node')

        self.bridge = CvBridge()
        self.latest_rgb = None
        self.latest_depth = None
        self.camera_info = None

        # Subscriptions
        self.create_subscription(Image, '/camera/image_raw', self.rgb_callback, 10)
        self.create_subscription(Image, '/camera/depth/image_raw', self.depth_callback, 10)
        self.create_subscription(CameraInfo, '/camera/camera_info', self.info_callback, 10)

        # TF2 Setup
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Service Server
        self.srv = self.create_service(DetectObjects, '/detect_objects', self.detect_objects_callback)

        self.get_logger().info("Object Detection Node initialized. Service /detect_objects ready.")

    def rgb_callback(self, msg):
        try:
            self.latest_rgb = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f"Failed to convert RGB image: {e}")

    def depth_callback(self, msg):
        try:
            # Handle float32 or 16UC1 depth encodings
            depth_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
            if depth_img.dtype == np.uint16:
                self.latest_depth = depth_img.astype(np.float32) / 1000.0
            else:
                self.latest_depth = depth_img
        except Exception as e:
            self.get_logger().error(f"Failed to convert Depth image: {e}")

    def info_callback(self, msg):
        if self.camera_info is None:
            self.camera_info = msg
            self.get_logger().info("Received Camera Info parameters.")

    def detect_objects_callback(self, request, response):
        if self.latest_rgb is None or self.latest_depth is None or self.camera_info is None:
            self.get_logger().warn("Sensor data not fully received yet.")
            response.success = False
            return response

        filter_color = request.filter_color.lower()
        hsv = cv2.cvtColor(self.latest_rgb, cv2.COLOR_BGR2HSV)

        # Define HSV Color Ranges
        color_masks = {}
        # Red (handles wrapping around 0/180)
        mask_red1 = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([10, 255, 255]))
        mask_red2 = cv2.inRange(hsv, np.array([170, 100, 100]), np.array([180, 255, 255]))
        color_masks['red'] = cv2.bitwise_or(mask_red1, mask_red2)
        # Blue
        color_masks['blue'] = cv2.inRange(hsv, np.array([100, 100, 100]), np.array([130, 255, 255]))
        # Green
        color_masks['green'] = cv2.inRange(hsv, np.array([35, 100, 100]), np.array([85, 255, 255]))

        fx = self.camera_info.k[0]
        fy = self.camera_info.k[4]
        cx = self.camera_info.k[2]
        cy = self.camera_info.k[5]

        detected_list = []
        obj_id_counter = 1

        for color_name, mask in color_masks.items():
            if filter_color != 'all' and filter_color != color_name:
                continue

            # Morphological noise removal
            kernel = np.ones((3, 3), np.uint8)
            cleaned_mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

            contours, _ = cv2.findContours(cleaned_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < 300:  # Ignore tiny noise artifacts
                    continue

                M = cv2.moments(cnt)
                if M['m00'] == 0:
                    continue

                u = int(M['m10'] / M['m00'])
                v = int(M['m01'] / M['m00'])

                # Sample depth Z
                if v >= self.latest_depth.shape[0] or u >= self.latest_depth.shape[1]:
                    continue
                z_depth = float(self.latest_depth[v, u])

                if math.isnan(z_depth) or z_depth <= 0.1 or z_depth > 3.0:
                    continue

                # 3D Point in Camera Optical Frame
                x_cam = (u - cx) * z_depth / fx
                y_cam = (v - cy) * z_depth / fy
                z_cam = z_depth

                # Create PoseStamped in camera optical frame
                cam_pose = PoseStamped()
                cam_pose.header.frame_id = self.camera_info.header.frame_id
                cam_pose.header.stamp = self.get_clock().now().to_msg()
                cam_pose.pose.position.x = x_cam
                cam_pose.pose.position.y = y_cam
                cam_pose.pose.position.z = z_cam
                cam_pose.pose.orientation.w = 1.0

                # Transform pose to base_link frame
                try:
                    transform = self.tf_buffer.lookup_transform(
                        'base_link',
                        cam_pose.header.frame_id,
                        rclpy.time.Time(),
                        timeout=rclpy.duration.Duration(seconds=1.0)
                    )
                    base_pose = tf2_geometry_msgs.do_transform_pose(cam_pose.pose, transform)

                    obj_msg = DetectedObject()
                    obj_msg.id = f"{color_name}_{obj_id_counter}"
                    obj_msg.color = color_name
                    obj_msg.pose = base_pose

                    # Distance from center of workspace (0, 0.25)
                    dist = math.sqrt((base_pose.position.x - 0.0)**2 + (base_pose.position.y - 0.25)**2)
                    obj_msg.distance_to_center = dist

                    detected_list.append(obj_msg)
                    obj_id_counter += 1

                except Exception as ex:
                    self.get_logger().error(f"TF Transform lookup failed: {ex}")

        # Sort objects by distance to workspace center
        detected_list.sort(key=lambda o: o.distance_to_center)

        response.success = True
        response.objects = detected_list
        self.get_logger().info(f"Detected {len(detected_list)} objects for filter '{filter_color}'.")
        return response

def main(args=None):
    rclpy.init(args=args)
    node = ObjectDetectionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
