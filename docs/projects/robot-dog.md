---
id: robot-dog
title: "Quadruped Robot Dog"
type: project
category: ai-ml
tree_icon: dog
videos:
  - https://youtu.be/OJbpN8ow_po
prerequisites: [ros2-basics, kinematics, 3d-printing, cpp-basics, robot-arm]
---

# Quadruped Robot Dog

Build a four-legged robot dog capable of dynamic walking, running, and adaptive terrain navigation using advanced kinematics and gait control.

## Project Overview

Quadruped robots represent a significant step up in complexity from wheeled platforms, requiring:
- Multi-leg inverse kinematics
- Gait planning and coordination
- Balance and stability control
- Terrain adaptation

## What You'll Build

- Assemble a quadruped robot chassis with 12+ servo motors (3 per leg)
- Implement inverse kinematics for leg control
- Develop gait patterns (trot, walk, gallop)
- Add IMU sensors for balance feedback
- Integrate autonomous navigation with ROS 2

## Required Knowledge

- Advanced robot kinematics (forward/inverse for multi-joint systems)
- ROS 2 control architecture
- C++ or Python for real-time control loops
- 3D printing for custom parts
- PID control and sensor fusion

## Popular Platforms

- **Stanford Pupper**: Open-source, affordable quadruped
- **Spot Micro**: 3D-printable Boston Dynamics Spot replica
- **Unitree Go1/A1**: Commercial platforms with SDK

## Key Challenges

- Coordinating 12 motors simultaneously
- Real-time gait computation
- Power management (quadrupeds draw significant current)
- Shock absorption and mechanical durability

## Resources

- [Stanford Pupper](https://stanfordstudentrobotics.org/pupper)
- [Spot Micro GitHub](https://github.com/mike4192/spotMicro)
- [Quadruped Kinematics Tutorial](https://www.researchgate.net/publication/332374021_Inverse_Kinematic_Analysis_Of_A_Quadruped_Robot)

## Iulia's Hardware Picks
- [Smart Dog Kit](https://amzn.to/45847B3)
- [Arduino starter kit](https://amzn.to/458MMrG) 
- [Raspberry Pico Starter Kit](https://amzn.to/4aWZL34)
