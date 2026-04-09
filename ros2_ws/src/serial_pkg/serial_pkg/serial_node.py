import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import serial
import time

class SerialNode(Node):
    def __init__(self):
        super().__init__('serial_node')

        self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        time.sleep(2)

        self.subscription = self.create_subscription(
            String, '/motor_cmd', self.send_cmd, 10)

    def send_cmd(self, msg):
        self.ser.write((msg.data + "\n").encode())


def main():
    rclpy.init()
    node = SerialNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()