import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
from geometry_msgs.msg import Twist
import math
import time


class DetectionNode(Node):
    def __init__(self):
        super().__init__('detection_node')

        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.alert_pub = self.create_publisher(
            String,
            '/detection_alert',
            10
        )

        self.cmd_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.last_alert_time = 0
        self.last_log_time = 0
        self.cooldown = 2.0

        self.get_logger().info("🚀 Detection node started (SMART mode - tuned)")

    def scan_callback(self, msg):
        ranges = msg.ranges

        mid = len(ranges) // 2
        front_ranges = ranges[mid - 30: mid + 30]

        valid = [
            r for r in front_ranges
            if not math.isinf(r) and not math.isnan(r)
        ]

        if not valid:
            return

        min_distance = min(valid)
        current_time = time.time()

        # 🔍 Clean logging (once per second)
        if current_time - self.last_log_time > 1.0:
            self.get_logger().info(f"Distance: {min_distance:.2f}")
            self.last_log_time = current_time

        # 🚨 CRITICAL → STOP
        if min_distance < 0.9:
            level = "🚨 CRITICAL: robot stopped"

            stop_msg = Twist()
            self.cmd_pub.publish(stop_msg)

        # ⚠️ WARNING
        elif min_distance < 1.8:
            level = "⚠️ WARNING"

        else:
            return

        # ⏱ Cooldown for alerts
        if current_time - self.last_alert_time > self.cooldown:
            alert_msg = String()
            alert_msg.data = f"{level} at {min_distance:.2f} m"

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