#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, LaserScan
from nav_msgs.msg import Odometry
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
import numpy as np
import math
import time


WAYPOINTS = [
    ( 5.0,  3.0),   # Checkpoint 1
    ( 5.0, -3.0),   # Checkpoint 2
    (-5.0, -3.0),   # Checkpoint 3 ← RED ZONE
    (-5.0,  3.0),   # Checkpoint 4
]

RED_ZONE_CHECKPOINT = 3

# Red zone is the area around Checkpoint 3 / Person B
RED_ZONE_CENTER = (-3.0, -1.5)
RED_ZONE_RADIUS = 4.0


class DetectionNode(Node):
    def __init__(self):
        super().__init__('detection_node')

        self.image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10
        )
        self.scan_sub = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10
        )
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10
        )
        self.checkpoint_sub = self.create_subscription(
            String, '/checkpoint_status', self.checkpoint_callback, 10
        )

        self.alert_pub = self.create_publisher(String, '/detection_alert', 10)
        self.bridge = CvBridge()

        self.humans = [
            {"name": "Person A (Safe Zone)", "x": 12.0, "y":  0.5},  # Checkpoint 1 area — safe
            {"name": "Person B (Red Zone)",  "x": -3.0, "y": -1.5},  # Checkpoint 3 area — RED
        ]

        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_yaw = 0.0       # ← added
        self.front_distance = float('inf')
        self.current_checkpoint = "Checkpoint 1"

        self.last_log_time = 0
        self.cooldown = 2.0
        self.last_lighting_time = 0
        self.lighting_cooldown = 2.0

        self.get_logger().info("🟢 [INFO] Monitoring system started")

    def odom_callback(self, msg):
        self.robot_x = msg.pose.pose.position.x
        self.robot_y = msg.pose.pose.position.y

        # ← added: track robot yaw so we know which way it's facing
        q = msg.pose.pose.orientation
        siny = 2.0 * (q.w * q.z + q.x * q.y)
        cosy = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.robot_yaw = math.atan2(siny, cosy)

        self._update_checkpoint_from_position()

    def _update_checkpoint_from_position(self):
        min_dist = float('inf')
        closest_idx = 0
        for i, (wx, wy) in enumerate(WAYPOINTS):
            d = math.sqrt((self.robot_x - wx)**2 + (self.robot_y - wy)**2)
            if d < min_dist:
                min_dist = d
                closest_idx = i
        self.current_checkpoint = f"Checkpoint {closest_idx + 1}"

    def checkpoint_callback(self, msg):
        self.current_checkpoint = msg.data

    def scan_callback(self, msg):
        ranges = msg.ranges
        front = ranges[:10] + ranges[-10:]
        valid = [r for r in front if not math.isinf(r) and not math.isnan(r)]
        if valid:
            self.front_distance = min(valid)

    def get_zone(self, human_x, human_y):
        # Zone is determined by WHERE THE HUMAN IS standing
        dist_to_red = math.sqrt(
            (human_x - RED_ZONE_CENTER[0])**2 +
            (human_y - RED_ZONE_CENTER[1])**2
        )
        if dist_to_red < RED_ZONE_RADIUS:
            return "RED"
        return "SAFE"

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_pink = np.array([140, 80, 80])
        upper_pink = np.array([170, 255, 255])
        mask = cv2.inRange(hsv, lower_pink, upper_pink)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        human_detected = False
        for cnt in contours:
            if cv2.contourArea(cnt) > 100:
                human_detected = True
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imshow("Camera Feed", frame)
        cv2.waitKey(1)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        self.process_lighting(brightness)
        self.process_logic(human_detected)

    def process_logic(self, human_detected):
        current_time = time.time()
        if current_time - self.last_log_time < self.cooldown:
            return

        self.publish(f"🟢 [INFO] Patrol active at {self.current_checkpoint}")

        if human_detected:
            # ← Pick human most directly in front of robot (camera line of sight)
            # not just the nearest one — avoids picking the wrong human
            def angle_to_human(h):
                dx = h["x"] - self.robot_x
                dy = h["y"] - self.robot_y
                angle_to = math.atan2(dy, dx)
                angle_diff = abs(math.atan2(
                    math.sin(angle_to - self.robot_yaw),
                    math.cos(angle_to - self.robot_yaw)
                ))
                return angle_diff  # smaller = more directly in front

            closest = min(self.humans, key=angle_to_human)

            distance = math.sqrt(
                (self.robot_x - closest["x"])**2 +
                (self.robot_y - closest["y"])**2
            )

            # Zone based on WHERE THE HUMAN IS, not the robot
            zone = self.get_zone(closest["x"], closest["y"])

            if zone == "RED":
                self.publish(
                    f"🔴 [CRITICAL] Intruder in RED ZONE (Checkpoint {RED_ZONE_CHECKPOINT}) | Distance: {distance:.2f} m"
                )
            else:
                self.publish(
                    f"🟡 [WARNING] Human detected at {self.current_checkpoint} (safe area) | Distance: {distance:.2f} m"
                )

        if self.front_distance < 1.0:
            self.publish(
                f"🟠 [ALERT] Obstacle blocking road at {self.front_distance:.2f} m"
            )

        self.last_log_time = current_time

    def process_lighting(self, brightness):
        current_time = time.time()
        if current_time - self.last_lighting_time < self.lighting_cooldown:
            return

        # Broken streetlight near Checkpoint 3 (-5, -3)
        dist_to_dark = math.sqrt(
            (self.robot_x - (-5.0))**2 + (self.robot_y - (-3.0))**2
        )
        if dist_to_dark < 2.0:
            brightness = 10.0
        elif dist_to_dark < 5.0:
            brightness = min(brightness, 45.0)

        if brightness < 30:
            self.publish(
                f"🔴 [CRITICAL] Very Low Visibility at {self.current_checkpoint} | Brightness: {brightness:.1f}"
            )
        elif brightness < 40:
            self.publish(
                f"🟡 [WARNING] Dim lighting at {self.current_checkpoint} | Brightness: {brightness:.1f}"
            )
        else:
            self.publish(
                f"🟢 [INFO] Lighting OK at {self.current_checkpoint} | Brightness: {brightness:.1f}"
            )

        self.last_lighting_time = current_time

    def publish(self, text):
        self.get_logger().info(text)
        msg = String()
        msg.data = text
        self.alert_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = DetectionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
