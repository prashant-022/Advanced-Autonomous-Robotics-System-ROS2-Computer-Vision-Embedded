# 🤖 Advanced Autonomous Robotics System (ROS2 + Computer Vision + Embedded)

An end-to-end robotics system integrating **computer vision, embedded systems, and ROS2-based architecture** for real-time perception, decision-making, and control.

---

## 📌 Overview

This project focuses on building a **modular robotics pipeline** that connects perception → planning → control using real hardware (Raspberry Pi + Arduino) and ROS2.

The system is designed to simulate real-world autonomous robotics challenges such as:
- Sensor noise & calibration
- Real-time processing constraints
- Hardware-software communication
- Decision-making under uncertainty

---

## 🧠 System Architecture


### Key Components:
- **Perception Layer**: Camera-based lane detection using OpenCV
- **Decision Layer**: Navigation logic & rule-based decision making
- **Control Layer**: Motor control via Arduino + PID
- **Communication**: Serial communication (UART) between Raspberry Pi and Arduino

---

## ⚙️ Tech Stack

- **Middleware**: ROS2 (Nodes, Topics, Messaging)
- **Languages**: Python, C++
- **Computer Vision**: OpenCV
- **Hardware**: Raspberry Pi 5, Arduino Uno
- **Simulation Tools**: Gazebo, RViz2
- **OS**: Ubuntu (Linux)

---

## 🔍 Features

- ✅ Real-time **lane detection using OpenCV**
- ✅ Modular **ROS2 node architecture**
- ✅ **Sensor data pipeline** with calibration and filtering
- ✅ **Arduino–Raspberry Pi communication system**
- ✅ **PID-based motor control**
- ✅ Designed for both **simulation and real-world deployment**

---

## 🎯 Key Challenges Solved

- Handling **sensor noise and inconsistent data**
- Ensuring **low-latency communication** between devices
- Synchronizing **multiple data streams**
- Debugging **hardware + software integration issues**

---

## 📊 Results

- Improved stability in robot navigation under variable lighting
- Achieved reliable communication between embedded systems
- Successfully tested perception-to-control pipeline in real-world setup

---

## 🎥 Demo

👉 [Add your demo video link here]

---

## 📁 Project Structure
/src
├── perception_node/
├── decision_node/
├── control_node/
/arduino
├── motor_control.ino
/config
/launch


---

## 🚀 How to Run

### Prerequisites:
- ROS2 (Iron or Humble)
- Ubuntu 22.04
- Python 3.x
- OpenCV

### Steps:

```bash
# Clone repo
git clone https://github.com/prashant-022/Advanced-Autonomous-Robotics-System-ROS2-Computer-Vision-Embedded.git

# Build workspace
colcon build

# Source workspace
source install/setup.bash

# Run nodes
ros2 launch package launch_file.py
