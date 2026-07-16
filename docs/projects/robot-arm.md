---
id: robot-arm
title: "Build a Robot Arm"
type: project
category: ai-ml
tree_icon: robot
prerequisites: [circuits, python-basics, mechanical-fundamentals, 3d-printing, kinematics, sensor-station]
video: https://www.youtube.com/playlist?list=PLA91EvK7Dr_t3BMHld1zLkzEQFPPG1A56
thumbnail: https://i.ytimg.com/vi/c6mrcNEFBoA/mqdefault.jpg
---

# Build a Robot Arm

Build a robot arm from scratch, progressing from cardboard prototypes to 3D-printed designs with AI-powered control using LeRobot.

## Project Evolution (7 Episodes)

### Episode 1: Basic Servo Control
- Connect 9g servo motors and potentiometers to Arduino
- Build first prototypes with cardboard and LEGO
- Simple real-time control through potentiometers

[![Episode 1](https://i.ytimg.com/vi/c6mrcNEFBoA/mqdefault.jpg)](https://youtu.be/c6mrcNEFBoA)

### Episode 2: Saved Positions
- Add buttons for pre-configured positions
- Improve arm structure with better materials
- Implement position memory and recall

[![Episode 2](https://i.ytimg.com/vi/xB-Buinw3lE/mqdefault.jpg)](https://youtu.be/xB-Buinw3lE)

### Episode 3: 3D Printing & MicroPython
- Switch to 3D-printed arm structure
- Upgrade to Raspberry Pi Pico for MicroPython support
- Add battery power with proper voltage regulation

[![Episode 3](https://i.ytimg.com/vi/xILy-UI7aAQ/mqdefault.jpg)](https://youtu.be/xILy-UI7aAQ)

### Episode 4: AI-Generated Movement
- Use GitHub Copilot to generate complex movement sequences
- Explore programmatic control patterns

[![Episode 4](https://i.ytimg.com/vi/aqYN7jCgId0/mqdefault.jpg)](https://youtu.be/aqYN7jCgId0)

### Episode 5: LeRobot SO101 Upgrade
- Upgrade to LeRobot SO101 3D-printed arms
- Switch to Feetech motors (professional-grade)
- Implement teleoperation and calibration

[![Episode 5](https://i.ytimg.com/vi/2hYSKIdKS9w/mqdefault.jpg)](https://youtu.be/2hYSKIdKS9w)

### Episode 6: Logging & Visualization
- Refactor code into production-quality Python
- Implement movement logging to JSON
- Visualize movements with Rerun

### Episode 7: Custom AI Policy
- Record custom dataset with LeRobot SDK
- Train policy on HuggingFace
- Deploy custom behavior (pick up dog toy)

## Required Knowledge

- Arduino/Raspberry Pi Pico programming
- Servo motor control and power management
- 3D printing and CAD (for custom parts)
- Python (MicroPython and standard)
- Robot kinematics (forward/inverse)
- Machine learning basics (for Episode 7)

## Hardware Used

- **Episode 1-2**: Arduino Uno, 9g servo motors, potentiometers, cardboard/LEGO
- **Episode 3-4**: Raspberry Pi Pico, 3D-printed frame, battery pack
- **Episode 5-7**: LeRobot SO101 kit, Feetech motors, Raspberry Pi

## Resources

- [Full GitHub Repository](https://github.com/iuliaferoli/robot_arm)
- [Robot Arm Playlist - Back To Engineering](https://www.youtube.com/playlist?list=PLA91EvK7Dr_t3BMHld1zLkzEQFPPG1A56)
- [LeRobot Documentation](https://github.com/huggingface/lerobot)
