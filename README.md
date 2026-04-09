# Advanced Autonomous Robotics System
### ROS2 · Computer Vision · Embedded Systems · Raspberry Pi 5

Building a full-stack autonomous car from scratch — perception, planning, and control — with real hardware and real constraints. This is not a simulation-only project. Everything here has been tested on physical hardware, debugged at 2 AM, and earned through iteration. 

Project at a glance:

<table align="center">
  <tr>
    <td align="center">
      <img src="images_videos/crashed.png" width="250"/><br>
      <b>Crashed</b>
    </td>
    <td align="center">
      <img src="images_videos/lag.png" width="250"/><br>
      <b>Avoided Crash (Lag)</b>
    </td>
    <td align="center">
      <img src="images_videos/final.png" width="250"/><br>
      <b>Final (No Lag)</b>
    </td>
  </tr>
</table>

---

## What this is

An end-to-end autonomous driving pipeline running on a Raspberry Pi 5 + Arduino Uno, built modularly so each layer — perception, decision, control — can be developed and tested independently.

The goal isn't just to make the car move. It's to understand *why* it moves, handle the edge cases, and build something that survives real-world noise.

Current progress: **Lane detection is working. The hardware has gone through two major revisions.**

---

## System Architecture (Lane Detection)
```
Camera Input
↓
Perception Layer  (OpenCV — lane detection, edge filtering)
↓
Decision Layer    (Navigation logic, rule-based control)
↓
Control Layer     (PID motor control)
↓
Arduino Uno  ←→  Raspberry Pi 5  (UART Serial)
↓
Motors + Encoders
```

**Stack:** Python · C++ · ROS2 (Jazzy) · OpenCV · Ubuntu 22.04 (Laptop) · Ubuntu 24.04 (Raspberry Pi 5)

**Hardware:** Raspberry Pi 5 · Arduino Uno · Encoder motors · Pi Camera

---

## Project Structure (Experiment, Debugging, Monitoring)
```
autonomous_car/
├── perception/       # Lane detection, camera pipeline, image preprocessing
├── vision/           # Vision utilities, frame handling
├── control/          # PID controller, motor commands
├── communication/    # Serial (UART) bridge between RPi and Arduino
├── firmware/         # Arduino code (C++)
├── configs/          # Tuning parameters, calibration values
├── experiment/       # Test scripts, exploratory work
├── cam_test.py       # Quick camera verification script
└── main.py           # Entry point
ros2_ws/              # ROS2 workspace (nodes, topics, launch files)
```
---

## Project Structure (ROS2 - Jazzy Workspace )
```bash
ros2_ws/src/
├── camera_pkg/       
├── lane_detection_pkg/   
├── control_pkg/ 
├── serial_pkg/   
├── localization_pkg/
├── planning_pkg/   
├── interfaces_pkg/ 
├── robot_bringup   
```

---

## Hardware Revisions

**v1 — Two BO motors + castor wheel (deprecated)**
- 300 RPM motors, no encoder feedback
- Castor at front — unstable at any real speed
- No speed control; direction-only
- Clean build but fundamentally limited

**v2 — Four-wheel drive with encoder motors (current)**
- Differential drive with 4 wheels
- Encoder feedback enables PID speed control
- Better stability, especially during turns
- Wiring is messier, capabilities are greater

---

## Key Engineering Challenges

**Sensor noise under variable lighting** — Lane detection breaks when lighting changes. The pipeline uses adaptive thresholding and region-of-interest masking to partially handle this. Still being improved.

**UART latency** — Serial communication between the Pi and Arduino introduces timing delays. Commands are batched and the control loop runs at a fixed frequency to manage this.

**Camera lag** — Frame pipeline had significant lag early on. Resolved by tuning buffer sizes and switching to a dedicated capture thread.

**PID tuning** — Encoder-based motors exposed how poorly the old setup was actually performing. Tuning the PID for straight-line tracking and cornering is ongoing.

---

## Setup and Running

### Prerequisites
- ROS2 Jazzy
- Ubuntu 24.04 LTS on Raspberry Pi 5
- Python 3.12 on raspberry Pi 5
- OpenCV (`pip install opencv-python`)
- PySerial (`pip install pyserial`)

### Steps

```bash
TO DO
```

---

## Current Status

- [x] Lane detection algorithm — working
- [x] Camera pipeline — stable
- [x] UART communication — stable
- [x] Hardware v2 (encoder motors) — assembled and tested
- [ ] PID tuning — in progress
- [ ] Full lane-following closed loop — in progress
- [ ] ROS2 node-based architecture — planned
- [ ] Obstacle detection — planned

---

## Notes

This repo will get messier before it gets cleaner. That's the nature of hardware projects — the `autonomous_car/` folder exists for a reason - experimental. Code gets committed as it works, not as it looks.

If you're building something similar and have questions, open an issue.
