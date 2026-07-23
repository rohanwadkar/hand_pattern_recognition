#!/usr/bin/env python3
import cv2
import mediapipe as mp
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class GestureRecognitionNode(Node):
    def __init__(self):
        super().__init__('gesture_recognition_node')

        # Parameters
        self.declare_parameter('webcam_index', 0)
        self.declare_parameter('debounce_frames', 15)
        self.declare_parameter('confidence_threshold', 0.7)

        self.webcam_idx = self.get_parameter('webcam_index').value
        self.debounce_required = self.get_parameter('debounce_frames').value
        self.confidence_thresh = self.get_parameter('confidence_threshold').value

        # Publisher
        self.publisher = self.create_publisher(String, '/gesture_command', 10)

        # MediaPipe Setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=self.confidence_thresh,
            min_tracking_confidence=self.confidence_thresh
        )
        self.mp_draw = mp.solutions.drawing_utils

        # Debouncing & Cooldown State Machine
        self.current_candidate = "NONE"
        self.candidate_counter = 0
        self.state = "IDLE"  # IDLE, ACCEPTED, COOLDOWN
        self.last_accepted_gesture = "NONE"

        # OpenCV Camera Setup
        self.cap = cv2.VideoCapture(self.webcam_idx)
        if not self.cap.isOpened():
            self.get_logger().error(f"Failed to open webcam at index {self.webcam_idx}")

        # Timer Loop (30 FPS)
        self.timer = self.create_timer(1.0 / 30.0, self.process_frame)
        self.get_logger().info("Gesture Recognition Node initialized. Listening to webcam...")

    def count_extended_fingers(self, landmarks):
        # Finger Tip vs PIP landmark indices in MediaPipe
        # Index: 8 vs 6, Middle: 12 vs 10, Ring: 16 vs 14, Pinky: 20 vs 18
        extended = 0

        # Index Finger
        if landmarks[8].y < landmarks[6].y:
            extended += 1
        # Middle Finger
        if landmarks[12].y < landmarks[10].y:
            extended += 1
        # Ring Finger
        if landmarks[16].y < landmarks[14].y:
            extended += 1
        # Pinky Finger
        if landmarks[20].y < landmarks[18].y:
            extended += 1

        return extended

    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            # If webcam fails (e.g. headless simulation mode), log warning
            return

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        detected_gesture = "NONE"

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                finger_count = self.count_extended_fingers(hand_landmarks.landmark)

                if finger_count == 1:
                    detected_gesture = "pick_and_place"
                elif finger_count == 2:
                    detected_gesture = "sort_by_color"
                elif finger_count == 3:
                    detected_gesture = "stack_objects"

        # Debouncing Logic
        if detected_gesture != "NONE":
            if detected_gesture == self.current_candidate:
                self.candidate_counter += 1
            else:
                self.current_candidate = detected_gesture
                self.candidate_counter = 1
        else:
            self.current_candidate = "NONE"
            self.candidate_counter = 0
            if self.state == "COOLDOWN":
                self.state = "IDLE"

        # Edge Trigger & Cooldown Logic
        if self.candidate_counter >= self.debounce_required:
            if self.state == "IDLE":
                self.state = "ACCEPTED"
                self.last_accepted_gesture = self.current_candidate

                # Publish Command
                msg = String()
                msg.data = self.current_candidate
                self.publisher.publish(msg)
                self.get_logger().info(f"GESTURE TRIGGERED: {self.current_candidate}")

                self.state = "COOLDOWN"

        # Visualization Feedback Overlay
        h, w, _ = frame.shape
        cv2.putText(frame, f"Detected: {detected_gesture}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        cv2.putText(frame, f"State: {self.state}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Progress bar for debouncing
        progress = min(1.0, self.candidate_counter / float(self.debounce_required))
        cv2.rectangle(frame, (10, 100), (10 + int(progress * 200), 120), (0, 255, 255), -1)
        cv2.rectangle(frame, (10, 100), (210, 120), (255, 255, 255), 2)

        cv2.imshow("Gesture Recognition Node", frame)
        cv2.waitKey(1)

    def destroy_node(self):
        if self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = GestureRecognitionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
