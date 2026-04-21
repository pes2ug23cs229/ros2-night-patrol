import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String


class PatrolNode(Node):
    def __init__(self):
        super().__init__('patrol_node')

        self.goal_pub = self.create_publisher(
            PoseStamped, '/goal_pose', 10
        )

        self.checkpoint_pub = self.create_publisher(
            String, '/checkpoint_status', 10
        )

        self.alert_sub = self.create_subscription(
            String, '/detection_alert', self.alert_callback, 10
        )

        self.checkpoints = [
            ("Checkpoint 1", 0.0, 0.0),
            ("Checkpoint 2", 4.0, 0.0),
            ("Checkpoint 3", 8.0, 0.0),
            ("Checkpoint 4", 12.0, 0.0),
        ]

        self.red_zone = ("Red Zone", 12.0, 0.5)

        self.current_index = 0
        self.cycle_count = 0
        self.intruder_detected = False

        self.get_logger().info("🚀 Patrol Node Started")

        # 🔥 TIMER INSTEAD OF WHILE LOOP
        self.timer = self.create_timer(8.0, self.patrol_step)

    # 🚨 detection input
    def alert_callback(self, msg):
        text = msg.data

        if "CRITICAL" in text or "Intruder" in text:
            self.get_logger().info("🚨 Intruder detected → going to RED ZONE")
            self.intruder_detected = True

    # 🚀 send goal
    def go_to(self, name, x, y):
        msg = PoseStamped()
        msg.header.frame_id = "map"
        msg.header.stamp = self.get_clock().now().to_msg()

        msg.pose.position.x = x
        msg.pose.position.y = y
        msg.pose.orientation.w = 1.0

        self.goal_pub.publish(msg)

        status = String()
        status.data = name
        self.checkpoint_pub.publish(status)

        self.get_logger().info(f"➡️ Moving to {name} ({x}, {y})")

    # 🔁 PATROL STEP (called every 8 sec)
    def patrol_step(self):

        # 🚨 priority override
        if self.intruder_detected:
            name, x, y = self.red_zone
            self.go_to(name, x, y)
            self.intruder_detected = False
            return

        # 🟢 normal patrol
        name, x, y = self.checkpoints[self.current_index]
        self.go_to(name, x, y)

        self.current_index += 1

        if self.current_index >= len(self.checkpoints):
            self.current_index = 0
            self.cycle_count += 1

        # 🔴 scheduled red zone
        if self.cycle_count >= 2:
            name, x, y = self.red_zone
            self.get_logger().info("🔴 Scheduled RED ZONE check")
            self.go_to(name, x, y)
            self.cycle_count = 0


def main(args=None):
    rclpy.init(args=args)
    node = PatrolNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
