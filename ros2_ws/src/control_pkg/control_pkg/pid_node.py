import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32, String

class PIDNode(Node):
    def __init__(self):
        super().__init__('pid_node')

        self.subscription = self.create_subscription(
            Int32, '/lane_error', self.control, 10)

        self.publisher = self.create_publisher(String, '/motor_cmd', 10)

        self.Kp = 0.001
        self.Kd = 0.0001
        self.Ki = 0.0

        self.prev_error = 0
        self.integral = 0

    def control(self, msg):
        error = msg.data
        dt = 0.02

        self.integral += error * dt
        derivative = (error - self.prev_error) / dt

        output = self.Kp*error + self.Ki*self.integral + self.Kd*derivative
        self.prev_error = error

        base = 140
        correction = int(output)
        correction = max(-40, min(40, correction))

        left = base - correction
        right = base + correction

        cmd = f"{left},{right}"
        self.publisher.publish(String(data=cmd))


def main():
    rclpy.init()
    node = PIDNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()