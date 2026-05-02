import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
import smbus
import time
import math
import tf_transformations

class IMUNode(Node):
    def __init__(self):
        super().__init__('imu_node')

        self.publisher = self.create_publisher(Imu, '/imu', 10)

        self.bus = smbus.SMBus(1)
        self.addr = 0x68
        self.bus.write_byte_data(self.addr, 0x6B, 0)

        self.alpha = 0.98
        self.roll = 0.0
        self.yaw = 0.0

        self.prev_time = time.time()

        self.calibrate()

        self.timer = self.create_timer(0.02, self.loop)

    def read_word(self, reg):
        high = self.bus.read_byte_data(self.addr, reg)
        low = self.bus.read_byte_data(self.addr, reg + 1)
        value = (high << 8) + low
        if value >= 0x8000:
            value = -((65535 - value) + 1)
        return value

    def get_accel(self):
        return (
            self.read_word(0x3B)/16384.0,
            self.read_word(0x3D)/16384.0,
            self.read_word(0x3F)/16384.0
        )

    def get_gyro(self):
        return (
            self.read_word(0x43)/131.0,
            self.read_word(0x45)/131.0,
            self.read_word(0x47)/131.0
        )

    def calibrate(self):
        self.get_logger().info("Calibrating IMU...")

        gx_off = gy_off = gz_off = 0
        samples = 500
        
        for _ in range(samples):
            gx, gy, gz = self.get_gyro()
            gx_off += gx
            gy_off += gy
            gz_off += gz
            time.sleep(0.005)

        self.gx_off = gx_off / samples
        self.gy_off = gy_off / samples
        self.gz_off = gz_off / samples
        
        self.get_logger().info(f"Gyro offsets: {self.gx_off:.3f}, {self.gy_off:.3f}, {self.gz_off:.3f}")

    def loop(self):
        msg = Imu()
        
        ### ROS time
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "imu_link"

        current_time = time.time()
        dt = current_time - self.prev_time
        self.prev_time = current_time

        ax, ay, az = self.get_accel()
        gx, gy, gz = self.get_gyro()

        gx -= self.gx_off
        gy -= self.gy_off
        gz -= self.gz_off
        
        # Convert gyro to radians/sec
        gx_rad = math.radians(gx)
        gy_rad = math.radians(gy)
        gz_rad = math.radians(gz)

        # Complementary filter (roll only)
        acc_roll = math.atan2(ay, az)
        gyro_roll = self.roll + gx_rad * dt
        self.roll = self.alpha * gyro_roll + (1 - self.alpha) * acc_roll

        ## Yaw integration
        self.yaw += gz_rad * dt

        # Quaternion
        q = tf_transformations.quaternion_from_euler(self.roll, 0.0, self.yaw)

        msg.orientation.x = q[0]
        msg.orientation.y = q[1]
        msg.orientation.z = q[2]
        msg.orientation.w = q[3]

        # Angular velocity (rad/s)
        msg.angular_velocity.x = gx_rad
        msg.angular_velocity.y = gy_rad
        msg.angular_velocity.z = gz_rad

        # Linear acceleration (m/s² approx, already in g → multiply if needed later)
        msg.linear_acceleration.x = ax
        msg.linear_acceleration.y = ay
        msg.linear_acceleration.z = az

        # Covariance (basic placeholder)
        msg.orientation_covariance = [
            0.05, 0, 0,
            0, 0.05, 0,
            0, 0, 0.05
        ]

        msg.angular_velocity_covariance = [
            0.02, 0, 0,
            0, 0.02, 0,
            0, 0, 0.02
        ]

        msg.linear_acceleration_covariance = [
            0.1, 0, 0,
            0, 0.1, 0,
            0, 0, 0.1
        ]

        self.publisher.publish(msg)


def main():
    rclpy.init()
    node = IMUNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()