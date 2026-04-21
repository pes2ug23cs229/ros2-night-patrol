#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from nav_msgs.msg import Odometry
import math
import threading

WAYPOINTS = [
    ( 5.0,  3.0),
    ( 5.0, -3.0),
    (-5.0, -3.0),
    (-5.0,  3.0),
]

class PatrolNode(Node):
    def __init__(self):
        super().__init__('patrol_node')

        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.checkpoint_pub = self.create_publisher(String, '/checkpoint_status', 10)

        self.timer = self.create_timer(0.1, self.loop)

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.wp_idx = 0

        self.create_subscription(Odometry, '/odom', self.odom_cb, 10)

        self.get_logger().info('🚗 Patrol started!')

        # Initial publish
        self.publish_checkpoint()

        # ✅ Wall-clock timer — fires every 5s regardless of sim time
        self._schedule_wall_publish()

    def _schedule_wall_publish(self):
        self._wall_timer = threading.Timer(5.0, self._wall_publish)
        self._wall_timer.daemon = True
        self._wall_timer.start()

    def _wall_publish(self):
        self.publish_checkpoint()
        self._schedule_wall_publish()  # reschedule

    def odom_cb(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        siny = 2.0*(q.w*q.z + q.x*q.y)
        cosy = 1.0 - 2.0*(q.y*q.y + q.z*q.z)
        self.yaw = math.atan2(siny, cosy)

    def publish_checkpoint(self):
        msg = String()
        msg.data = f"Checkpoint {self.wp_idx + 1}"
        self.checkpoint_pub.publish(msg)
        self.get_logger().info(f"📍 Publishing: {msg.data}")

    def loop(self):
        if self.wp_idx >= len(WAYPOINTS):
            self.wp_idx = 0
            self.publish_checkpoint()

        tx, ty = WAYPOINTS[self.wp_idx]
        dx = tx - self.x
        dy = ty - self.y
        dist = math.sqrt(dx*dx + dy*dy)

        target_yaw = math.atan2(dy, dx)
        yaw_err = math.atan2(
            math.sin(target_yaw - self.yaw),
            math.cos(target_yaw - self.yaw)
        )

        msg = Twist()

        if dist < 0.8:
            self.get_logger().info(f'✅ Reached waypoint {self.wp_idx + 1}')
            self.wp_idx += 1
            self.publish_checkpoint()

        elif abs(yaw_err) > 0.3:
            msg.angular.z = 1.2 if yaw_err > 0 else -1.2

        else:
            msg.linear.x = min(0.55, dist * 0.5)
            msg.angular.z = yaw_err * 0.8

        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = PatrolNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
