import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Int32
from cv_bridge import CvBridge
import cv2
import numpy as np

class LaneNode(Node):
    def __init__(self):
        super().__init__('lane_node')

        self.bridge = CvBridge()

        self.subscription = self.create_subscription(
            Image, '/image_raw', self.process, 10)

        self.publisher = self.create_publisher(Int32, '/lane_error', 10)

        self.alpha = 0.2
        self.smooth_error = None

    def process(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')

        h, w, _ = frame.shape
        center_x = w // 2

        roi = frame[int(h*0.1):int(h*0.65), :]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        hist = np.sum(edges, axis=0)

        if np.max(hist) > 0:
            lane_center = int(np.argmax(hist))
            error = lane_center - center_x

            if self.smooth_error is None:
                self.smooth_error = error
            else:
                self.smooth_error = int(
                    self.alpha * error + (1-self.alpha)*self.smooth_error
                )

            self.publisher.publish(Int32(data=self.smooth_error))


def main():
    rclpy.init()
    node = LaneNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()