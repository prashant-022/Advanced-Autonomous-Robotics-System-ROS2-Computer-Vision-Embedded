import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32MultiArray
import serial
import time

class EncoderNode(Node):
    def __init__(self):
        super().__init__('encoder_node')

        self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        time.sleep(2)
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        self.ser.write(b"RESET\n")
        time.sleep(0.5)
        
        self.get_logger().info("Encoder RESET sent")

        self.publisher = self.create_publisher(
            Int32MultiArray,
            '/encoder',
            10
        )

        self.timer = self.create_timer(0.02, self.read_encoder)

    def read_encoder(self):
        if self.ser.in_waiting:
            line = self.ser.readline().decode().strip()
            
            if "RESET" in line:
                return

            try:
                left, right = map(int, line.split(','))

                msg = Int32MultiArray()
                msg.data = [left, right]

                self.publisher.publish(msg)

                self.get_logger().info(f"L:{left} R:{right}")

            except:
                pass


def main():
    rclpy.init()
    node = EncoderNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()