# Energy-Free Step Counting using Photovoltaic Sensors

This repository contains the implementation of an **energy-free step counting system** based on the research published on **arXiv**:  

## 🚀 Overview
This project explores how **photovoltaic (solar) cells** can be used as **sensors** for detecting steps in a power-efficient manner. The system leverages variations in light intensity detected by foot-mounted solar cells to recognize step patterns, ensuring **accurate step counting without the need for external power sources**.

## 🎥 Step Detection Demo
[![Watch the Video](https://img.youtube.com/vi/VIDEO_ID/0.jpg)](https://github.com/k-shintani/EnergyFreeStepCounting/blob/main/demo.mp4)

Click the thumbnail above to watch the video.

## 📌 Features
- **Photovoltaic-based sensing** for step detection.
- **Real-time processing** of sensor data.
- **Automatic correction** for missed steps.
- **CSV-based data logging** for further analysis.

## 📊 Step Data Format

This repository includes two sample datasets recorded during walking:

- **left.csv**: Contains photovoltaic voltage readings from the left foot sensor.
- **right.csv**: Contains photovoltaic voltage readings from the right foot sensor.

### 📁 CSV Data Format

Each CSV file contains three columns:

| Column Name              | Data Type | Description |
|--------------------------|----------|-------------|
| **Timestamp**            | `float`  | Unix time in seconds. |
| **Photo-Voltage_Center** | `int`    | Voltage reading from the center of the foot-mounted photovoltaic sensor. |
| **Photo-Voltage_Outside**| `int`    | Voltage reading from the outer side of the foot-mounted photovoltaic sensor. |

These data files are used as input to process real-time step detection.

---

For further details on data processing and step detection, please refer to the documentation.
