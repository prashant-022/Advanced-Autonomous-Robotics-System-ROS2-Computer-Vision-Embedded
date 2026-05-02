import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32MultiArray
from nav_msgs.msg import Odometry
import math
import time
import tf_transformations

class OdometryNode(Node):
    def __init__(self):
        super().__init__('odometry_node')

        self.subscription = self.create_subscription(
            Int32MultiArray,
            '/encoder',
            self.callback,
            10
        )

        self.publisher = self.create_publisher(Odometry, '/odom', 10)

        # Robot parameters (VERY IMPORTANT)
        self.wheel_radius = 0.035      # meters (adjust)
        self.wheel_base = 0.17         # distance between wheels (meters)
        self.ticks_per_rev = 350        # adjust based on encoder

        # State
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0

        self.prev_left = 0
        self.prev_right = 0
        self.prev_time = time.time()

    def callback(self, msg):
        left_ticks, right_ticks = msg.data

        current_time = time.time()
        dt = current_time - self.prev_time
        self.prev_time = current_time

        if dt == 0:
            return

        # Convert ticks → distance
        dl = (left_ticks - self.prev_left) * (2 * math.pi * self.wheel_radius / self.ticks_per_rev)
        dr = (right_ticks - self.prev_right) * (2 * math.pi * self.wheel_radius / self.ticks_per_rev)

        self.prev_left = left_ticks
        self.prev_right = right_ticks

        # Robot motion
        dc = (dl + dr) / 2.0
        dtheta = (dr - dl) / self.wheel_base

        # Update pose
        self.x += dc * math.cos(self.theta)
        self.y += dc * math.sin(self.theta)
        self.theta += dtheta
        
         # Normalize theta
        self.theta = math.atan2(math.sin(self.theta), math.cos(self.theta))

        # Velocities
        v = dc / dt
        omega = dtheta / dt

        # Create message
        odom = Odometry()

        # Header
        odom.header.stamp = self.get_clock().now().to_msg()
        odom.header.frame_id = "odom"
        odom.child_frame_id = "base_link"

        # Position
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y

        q = tf_transformations.quaternion_from_euler(0, 0, self.theta)

        odom.pose.pose.orientation.x = q[0]
        odom.pose.pose.orientation.y = q[1]
        odom.pose.pose.orientation.z = q[2]
        odom.pose.pose.orientation.w = q[3]

        # Velocity
        odom.twist.twist.linear.x = v
        odom.twist.twist.angular.z = omega

        # Covariance (basic placeholder)
        odom.pose.covariance = [
            0.05, 0, 0, 0, 0, 0,
            0, 0.05, 0, 0, 0, 0,
            0, 0, 99999, 0, 0, 0,
            0, 0, 0, 99999, 0, 0,
            0, 0, 0, 0, 99999, 0,
            0, 0, 0, 0, 0, 0.1
        ]

        odom.twist.covariance = [
            0.1, 0, 0, 0, 0, 0,
            0, 0.1, 0, 0, 0, 0,
            0, 0, 99999, 0, 0, 0,
            0, 0, 0, 99999, 0, 0,
            0, 0, 0, 0, 99999, 0,
            0, 0, 0, 0, 0, 0.2
        ]

        self.publisher.publish(odom)

        self.get_logger().info(f"x:{self.x:.2f} y:{self.y:.2f} θ:{self.theta:.2f}")


def main():
    rclpy.init()
    node = OdometryNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()