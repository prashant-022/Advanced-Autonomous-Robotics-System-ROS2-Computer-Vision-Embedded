import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class CameraNode(Node):
    def __init__(self):
        super().__init__('camera_node')

        self.publisher = self.create_publisher(Image, '/image_raw', 10)
        self.bridge = CvBridge()

        pipeline = (
            "libcamerasrc ! "
            "video/x-raw,width=640,height=480,format=YUY2,framerate=30/1 ! "
            "queue max-size-buffers=1 leaky=downstream ! "
            "appsink drop=true max-buffers=1 sync=false"
        )

        self.cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

        self.timer = self.create_timer(0.03, self.publish_frame)

    def publish_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR_YUY2)
        msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
        self.publisher.publish(msg)


def main():
    rclpy.init()
    node = CameraNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()