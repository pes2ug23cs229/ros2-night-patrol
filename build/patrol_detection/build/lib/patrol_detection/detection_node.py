import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
import math
import time


class DetectionNode(Node):
    def __init__(self):
        super().__init__('detection_node')

        # Subscribe to LiDAR topic
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        # Publisher for alerts
        self.publisher = self.create_publisher(
            String,
            '/detection_alert',
            10
        )

        # Cooldown timer (seconds)
        self.last_alert_time = 0
        self.cooldown = 2.0

        self.get_logger().info("🚀 Detection node started (LiDAR mode)")

    def scan_callback(self, msg):
        # Filter valid distances
        valid_ranges = [
            r for r in msg.ranges
            if not math.isinf(r) and not math.isnan(r)
        ]

        if not valid_ranges:
            return

        min_distance = min(valid_ranges)

        current_time = time.time()

        # Detection logic with cooldown
        if min_distance < 1.0 and (current_time - self.last_alert_time > self.cooldown):
            alert_msg = String()
            alert_msg.data = f"⚠️ Obstacle detected at {min_distance:.2f} meters"

            self.get_logger().info(alert_msg.data)
            self.publisher.publish(alert_msg)

            self.last_alert_time = current_time


def main(args=None):
    rclpy.init(args=args)
    node = DetectionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()