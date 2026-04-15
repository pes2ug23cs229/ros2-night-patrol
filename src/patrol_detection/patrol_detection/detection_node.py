import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, LaserScan
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
import math
import time


class DetectionNode(Node):
    def __init__(self):
        super().__init__('detection_node')

        # Camera
        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        # LiDAR
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        # Alerts
        self.alert_pub = self.create_publisher(
            String,
            '/detection_alert',
            10
        )

        self.bridge = CvBridge()

        self.prev_frame = None
        self.motion_detected = False
        self.min_distance = float('inf')

        self.last_alert_time = 0
        self.last_log_time = 0

        self.cooldown = 2.0

        self.get_logger().info("🚀 Fusion detection node started (DEMO MODE)")

    # 📸 CAMERA
    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self.prev_frame is not None:
            diff = cv2.absdiff(self.prev_frame, gray)
            _, thresh = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)

            motion = cv2.countNonZero(thresh)

            # 🔥 DEMO threshold (easy trigger)
            self.motion_detected = motion > 500

            # show motion visually (white areas)
            cv2.imshow("Motion", thresh)

        self.prev_frame = gray

        cv2.imshow("Camera Feed", frame)
        cv2.waitKey(1)

        self.check_alert()

    # 📡 LIDAR
    def scan_callback(self, msg):
        valid = [
            r for r in msg.ranges
            if not math.isinf(r) and not math.isnan(r)
        ]

        if valid:
            self.min_distance = min(valid)

        self.check_alert()

    # 🚨 FUSION LOGIC
    def check_alert(self):
        current_time = time.time()

        # 🔍 clean logging (once per sec)
        if current_time - self.last_log_time > 1.0:
            self.get_logger().info(
                f"Motion: {self.motion_detected}, Distance: {self.min_distance:.2f}"
            )
            self.last_log_time = current_time

        # 🔥 DEMO thresholds
        if (
            self.motion_detected and
            self.min_distance < 2.0 and
            (current_time - self.last_alert_time > self.cooldown)
        ):
            alert_msg = String()
            alert_msg.data = f"🚨 ALERT! Motion + object at {self.min_distance:.2f} m"

            self.get_logger().info(alert_msg.data)
            self.alert_pub.publish(alert_msg)

            self.last_alert_time = current_time


def main(args=None):
    rclpy.init(args=args)
    node = DetectionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()