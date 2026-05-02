from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([

        Node(
            package='camera_pkg',
            executable='camera_node',
            name='camera_node',
            output='screen'
        ),
        
        Node(
            package='lane_detection_pkg',
            executable='lane_node',
            name='lane_node',
            output='screen'
        ),
        
        Node(
            package='control_pkg',
            executable='pid_node',
            name='pid_node',
            output='screen'
        ),
            
        Node(
            package='serial_pkg',
            executable='serial_node',
            name='serial_node',
            output='screen'
        ),  
        
        Node(
            package='serial_pkg',
            executable='encoder_node',
            name='encoder_node',
            output='screen'
        ), 
        
        Node(
            package='control_pkg',
            executable='odometry_node',
            name='odometry_node',
            output='screen'
        ), 
        
        Node(
            package='imu_pkg',
            executable='imu_node',
            name='imu_node',
            output='screen'
        ), 
        
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=['/home/pras/ros2_ws/src/robot_bringup/config/ekf.yaml']
        ), 
        
    ])