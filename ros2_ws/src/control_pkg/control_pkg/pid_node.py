import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32, String
import time

class PIDNode(Node):
    def __init__(self):
        super().__init__('pid_node')

        self.subscription = self.create_subscription(
            Int32, '/lane_error', self.control, 10)

        self.publisher = self.create_publisher(String, '/motor_cmd', 10)
        
        ## PID params (updated)
        self.Kp = 0.05
        self.Kd = 0.01
        self.Ki = 0.0

        self.prev_error = 0
        self.integral = 0
        
        ## Motor smoothing:
        self.prev_left = 0
        self.prev_right = 0
        self.alpha_motor = 0.7
        
        ## Startup delay:
        self.start_time = time.time()
        self.STARTUP_DELAY = 3.0
        
        ## Lane lost handling:
        self.last_seen_time = time.time()
        self.LANE_TIMEOUT = 0.5                 ## Seconds
        
        ## LAST Command:
        self.last_left = 0
        self.last_right = 0
        
        ## State machine:
        self.state = "STOP"

    def control(self, msg):
        current_time = time.time()
        
        # Startup
        if current_time - self.start_time < self.STARTUP_DELAY:
            self.publisher.publish(String(data="0,0"))
            return
        
        error = msg.data
        # error = error/2
        self.last_seen_time = current_time
                
        ## State --> Drive:
        self.state = "DRIVE"
        
        ## PID:
        dt = 0.02
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt

        output = self.Kp*error + self.Ki*self.integral + self.Kd*derivative
        self.prev_error = error

        correction = output
                
        ## Dead zone:
        if abs(correction) < 5:
            correction = 0
            
        ## Limit correction:
        correction = int(max(-40, min(40, correction)))
        
        ## Speed control
        turn_strength = abs(correction)
        base_speed = int(120 - turn_strength*0.7) 
        
        ## Clamp:
        base_speed = max(70, min(130, base_speed))
        
        ## Motor output:
        left = base_speed - correction
        right = base_speed + correction
        
        ## Clamp motor outputs:
        left = max(0, min(255, left))
        right = max(0, min(255, right))

        ## motor smoothing:
        left = int(self.alpha_motor * self.prev_left + (1 - self.alpha_motor) * left)
        right = int(self.alpha_motor * self.prev_right + (1 - self.alpha_motor) * right)

        self.prev_left = left
        self.prev_right = right
        
        # self.last_left = left
        # self.last_right = right
        
        cmd = f"{left},{right}"
        self.publisher.publish(String(data=cmd))
        
        self.get_logger().info(f"L: {left} R: {right} | Error: {error}")
        
    def state_manager(self):
        current_time = time.time()

        if current_time - self.last_seen_time > 1.5:
            self.state = "SEARCH"
        elif current_time - self.last_seen_time > self.LANE_TIMEOUT:
            self.state = "LOST"
        else:
            return  # IMPORTANT → don't override DRIVE
    
    
    def main_loop(self):
        current_time = time.time()

        if current_time - self.last_seen_time > 1.5:
            self.publisher.publish(String(data="80,-80"))
            self.get_logger().warn("[SEARCH] Rotating")

        elif current_time - self.last_seen_time > self.LANE_TIMEOUT:
            self.publisher.publish(String(data="80,80"))
            self.get_logger().warn("[LOST] Slow forward")

def main():
    rclpy.init()
    node = PIDNode()
    node.create_timer(0.1, node.main_loop)
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()