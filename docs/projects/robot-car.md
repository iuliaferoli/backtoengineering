---
id: robot-car
title: "Autonomous Robot Car"
type: project
category: ai-ml
tree_icon: car
prerequisites: [ros2-basics, computer-vision, slam, circuits]
video: https://www.youtube.com/playlist?list=PLA91EvK7Dr_uZfC8QRWU6ETB3tA66958w
---

# Autonomous Robot Car

Build a self-driving car capable of lane detection, obstacle avoidance, and autonomous navigation using computer vision and SLAM.

## Project Overview

A robot car combines wheeled mobility with vision-based autonomy, making it an ideal platform for learning:
- Lane following algorithms
- Object detection and tracking
- Path planning and control
- Sensor fusion (camera + ultrasonic/LiDAR)

## What You'll Build

- Assemble a 4-wheel drive robot chassis with motor drivers
- Mount camera and distance sensors
- Implement lane detection with OpenCV
- Add SLAM for mapping and localization
- Deploy autonomous navigation with ROS 2 Nav2

## Required Knowledge

- Arduino or Raspberry Pi programming
- Computer vision (OpenCV, lane detection, object tracking)
- ROS 2 navigation stack
- Basic electronics (motor control, sensor wiring)
- Path planning algorithms (A*, Dijkstra)

## Popular Kits & Platforms

- **Elegoo Smart Robot Car** (Arduino-based, beginner-friendly)
- **JetBot** (NVIDIA Jetson Nano, AI-powered)
- **DonkeyCar** (RC car platform with autonomous racing)
- **F1/10 Autonomous Racing** (university-level competition platform)

## Key Features to Implement

1. **Basic mobility**: Motor control, encoder feedback
2. **Obstacle avoidance**: Ultrasonic sensors, basic reactive control
3. **Lane following**: Camera-based line detection
4. **Mapping**: SLAM with 2D LiDAR
5. **Autonomy**: Waypoint navigation, traffic sign recognition

## Resources

- [Microcontroller Basics Playlist - Back To Engineering](https://www.youtube.com/playlist?list=PLA91EvK7Dr_uZfC8QRWU6ETB3tA66958w)
- [DonkeyCar Documentation](https://docs.donkeycar.com/)
- [JetBot GitHub](https://github.com/NVIDIA-AI-IOT/jetbot)
- [F1/10 Autonomous Racing](https://f1tenth.org/)
