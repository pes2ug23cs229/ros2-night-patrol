# 🚔 Night Patrol Robot System 🤖

## 📌 Overview

This project simulates an **autonomous night patrol robot** using **ROS2 and Gazebo**.
The robot continuously patrols predefined checkpoints, monitors the environment using camera and LiDAR sensors, and generates intelligent alerts based on:

* Human presence
* Zone classification (Safe / Red Zone)
* Lighting conditions
* Obstacles

The system provides a **real-time monitoring dashboard** through structured logs.

---

## 🧠 Key Features

### 👤 Human Detection

* Implemented using **OpenCV (HSV color segmentation + contour detection)**
* Detects humans marked with a distinct color (pink in simulation)
* Works at different distances from the robot

---

### 🚨 Zone Classification (Coordinate-Based)

* Environment divided into:

  * **Safe Zone**
  * **Red Zone (High Risk Area)**
* Based on predefined map coordinates
* Alerts depend on **human location (not robot position)**

---

### 💡 Adaptive Lighting Detection

* Uses camera feed → converted to grayscale
* Computes **average brightness**
* Classifies lighting into 3 levels:

| Level       | Condition        | Output              |
| ----------- | ---------------- | ------------------- |
| 🟢 Normal   | Brightness > ~40 | Lighting OK         |
| 🟡 Warning  | 30–40            | Dim lighting        |
| 🔴 Critical | < 30             | Very Low Visibility |

---

### 📡 Obstacle Detection (LiDAR)

* Uses `/scan` topic (LaserScan)
* Detects closest object in front of robot
* Helps identify obstacles blocking path

---

### 🧭 Patrol System (Checkpoint-Based)

* Robot moves through predefined waypoints:

  * Checkpoint 1 → 2 → 3 → 4 → loop
* Publishes checkpoint updates
* Detection system uses this for contextual alerts

---

### 📊 Live Monitoring Dashboard

System generates structured real-time logs:

```text
🟢 [INFO] Patrol active at Checkpoint X

🟢 [INFO] Lighting OK at Checkpoint X | Brightness: 43.5
🟡 [WARNING] Dim lighting at Checkpoint X | Brightness: 35.5
🔴 [CRITICAL] Very Low Visibility at Checkpoint X | Brightness: 29.8

🟡 [WARNING] Human detected at Checkpoint X (safe area) | Distance: 12.5 m
🔴 [CRITICAL] Intruder in RED ZONE (Checkpoint 3) | Distance: 5.0 m

🟠 [ALERT] Obstacle blocking road at 0.97 m
```

---

## ⚙️ Tech Stack

* ROS2 (Jazzy)
* Gazebo (Simulation)
* Python (rclpy)
* OpenCV
* cv_bridge
* NumPy

---

## 🧠 System Architecture

```
Camera → Human Detection + Lighting Analysis
LiDAR → Obstacle Detection
Odometry → Robot Position Tracking
Patrol Node → Checkpoint Publishing
↓
Detection Node → Decision Logic
↓
Monitoring Dashboard → Alerts
```

---

## 🚀 How to Run

### 1️⃣ Navigate to workspace

```bash
cd /mnt/c/Users/LENOVO/OneDrive/Desktop/ros2_ws
```

---

### 2️⃣ Build workspace

```bash
colcon build --symlink-install
```

---

### 3️⃣ Source environment

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
```

---

### 4️⃣ Run system (4 terminals)

#### 🟢 Terminal 1 – World

```bash
ros2 launch night_patrol_world city_world.launch.py
```

#### 🟡 Terminal 2 – Robot Navigation

```bash
ros2 launch night_patrol_robot robot_nav.launch.py
```

#### 🔵 Terminal 3 – ROS-Gazebo Bridge

```bash
ros2 run ros_gz_bridge parameter_bridge ...
```

#### 🔴 Terminal 4 – Detection System

```bash
ros2 run patrol_detection detection_node
```

---

## 👥 Contributors

* **Jenifer Sajit** – Simulation Environment
  (Gazebo world, roads, buildings, humans, lighting setup)

* **J Sai Vihitha** – Robot Navigation & Patrol
  (Waypoint movement, checkpoint publishing)

* **Ishaani Shetty** – Detection & Monitoring System
  (Human Detection, Lighting Analysis, Zone Classification, Alerts)

* **Greeshma Dhananjaiah** – System Integration
  (ROS-Gazebo bridge, topics, sensor integration)

---

## ⚠️ Limitations

* Human detection is **color-based** (not AI-based)
* Sensitive to lighting changes and color variations
* Humans are **static** in simulation (no real tracking)
* Lighting detection uses **simple brightness threshold**
* No deep learning model (e.g., YOLO)

---

## 🔮 Future Improvements

* AI-based human detection (YOLO / CNN)
* Dynamic human movement tracking
* Smarter patrol planning (priority-based navigation)
* Advanced lighting analysis
* Multi-human tracking system

---

## 🎯 Conclusion

This system demonstrates a **complete perception + monitoring pipeline** for an autonomous patrol robot, combining:

* Computer Vision
* Sensor Fusion
* Real-time decision making
* Structured alert generation

It showcases how robots can intelligently monitor environments and respond based on context.

---
