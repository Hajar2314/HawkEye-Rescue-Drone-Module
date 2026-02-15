# HawkEye — Rescue Drone Module

[![GitHub](https://img.shields.io/badge/GitHub-Hajar2314%2FHawkEye--Rescue--Drone--Module-blue?logo=github)](https://github.com/Hajar2314/HawkEye-Rescue-Drone-Module)

An autonomous onboard perception module for UAVs that detects people, confirms presence with thermal imaging, logs GPS location, and deploys a payload — all accessible through a live web interface from any device on the network.

Built for **PatriotHacks 2026** at George Mason University.

### Team
| Name | GitHub |
|---|---|
| Tan Chau | [@tanchau](https://github.com/tanchau) |
| Hajar Alzahrani | [@Hajar2314](https://github.com/Hajar2314) |
| Vishvajit Senthilkumar | — |
| Robert Haas | — |

---

## What It Does

1. **Streams live video** from a Raspberry Pi Camera (CSI) through a browser-accessible web interface
2. **Runs YOLOv8 object detection** on every 6th frame to identify people in real time
3. **Tracks and assigns IDs** (P1, P2, P3...) to each detected person across frames
4. **Lock-on targeting** — once a person enters the central drop zone and holds for 3 seconds, the system locks on
5. **Captures synchronized evidence** on each detection and drop event:
   - RGB photo snapshot
   - Thermal heatmap image (MLX90640)
   - GPS coordinates (NEO-6M)
   - Timestamp
   - JSON metadata sidecar
6. **Deploys payload** via two servo motors, either manually (operator approval) or automatically on lock confirmation
7. **Logs everything** — mission log, drop history, and a full photo gallery accessible in the browser

---

## Why This Exists

In search and rescue, the hardest part isn't reaching someone — it's finding them fast enough. Drones can scan large areas from above, but pilots still have to manually spot a person on a video feed.

HawkEye makes the drone understand what it sees. It combines visible-light detection with thermal confirmation so the system can autonomously identify a human presence, record their location, and deploy help — without the pilot having to notice them first.

The goal is a lightweight attachable module that works on any UAV or mobile robot without modifying the vehicle itself.

---

## Hardware

| Component | Purpose |
|---|---|
| Raspberry Pi 5 | Main compute — runs Flask, YOLO, all sensor threads |
| Raspberry Pi Camera (IMX219) | Primary RGB video stream via CSI |
| MLX90640 Thermal Camera | Thermal confirmation + heatmap capture (I2C) |
| NEO-6M GPS Module | Location stamping on captures (UART serial) |
| 2× SG90 Servo Motors | Payload drop mechanism (GPIO PWM) |
| 5V / 5A USB-C Power Supply | Required — Pi 5 + servos + camera demand stable power |

> **Note on power:** Servos draw current spikes when moving. Use a dedicated 5V/5A supply, not a standard USB power bank, to avoid brownouts during drops.

---

## Software Stack

| Library | Role |
|---|---|
| Python 3 | Core language |
| Flask | Web server and REST API |
| Picamera2 | Pi Camera capture (replaces OpenCV VideoCapture) |
| OpenCV | Frame processing, bounding box rendering, JPEG encoding |
| Ultralytics YOLOv8 | Person detection (`yolov8n.pt`) |
| adafruit-circuitpython-mlx90640 | Thermal sensor reading |
| Matplotlib | Thermal heatmap PNG generation |
| pyserial | GPS NMEA sentence parsing |
| gpiozero + lgpio | Servo PWM control |

---

## Project Structure

```
rescue-drone/
├── app.py              # Main application — Flask server, YOLO, all sensor threads
├── dropper.py          # Servo control module (initialize, hold, drop sequence)
├── yolov8n.pt          # YOLOv8 nano model weights
├── captures/           # Auto-created — RGB snapshots + JSON sidecars
│   ├── P1_det_20260215_143012.jpg    # Detection photo (first sight of person)
│   ├── P1_det_20260215_143012.json   # Metadata: GPS, thermal, timestamp, event
│   ├── P1_drp_20260215_143045.jpg    # Drop photo (payload released)
│   └── P1_drp_20260215_143045.json
└── heatmap_images/     # Auto-created — thermal heatmap PNGs per event
    └── heatmap_20260215_143012.png
```

---

## Installation

### 1. Clone and enter the project

```bash
git clone https://github.com/Hajar2314/HawkEye-Rescue-Drone-Module.git
cd rescue-drone
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install flask ultralytics opencv-python picamera2 \
            adafruit-circuitpython-mlx90640 matplotlib \
            pyserial gpiozero lgpio
```

> On Raspberry Pi OS, if you get externally-managed-environment errors, add `--break-system-packages` or use the venv approach above.

### 4. Download YOLOv8 weights

```bash
# The model downloads automatically on first run, or manually:
python3 -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

---

## Running

```bash
# From within the project directory with venv active:
python3 app.py
```

Then open a browser on any device connected to the same network:

```
http://<raspberry-pi-ip>:5000
```

> **Tip:** Use your phone's hotspot instead of university/campus Wi-Fi. Most university networks use client isolation which blocks device-to-device connections.

To find the Pi's IP address:
```bash
hostname -I
```

---

## Web Interface

### Main Dashboard (`/`)

| Panel | Description |
|---|---|
| **Live Feed** | Full-frame video stream with YOLO bounding boxes, targeting reticle, and mode overlay |
| **Live Telemetry** | FPS, person count, detection confidence, drop counter |
| **Drop Mode** | Toggle between MANUAL (operator approves drop) and AUTO (drops on lock) |
| **Target Lock** | Progress bar — fills over 3 seconds when a person is centered in the drop zone |
| **Payload Release** | Manual drop button, activates when locked on |
| **GPS Position** | Live lat/lon/alt from NEO-6M — shows FIX ✓ / NO FIX status |
| **Sensor Status** | Live indicators for Thermal and Servo hardware |
| **Mission Log** | Timestamped event feed (detections, locks, drops) |
| **Mission Control** | NEW MISSION button — resets person IDs to P1 and wipes all capture files |
| **Captures** | Running list of detection and drop photos with GPS and thermal tags |

### Gallery (`/gallery`)

Full photo browser with:
- Filter by event type (All / Detections / Drops)
- Sort by newest, oldest, or person ID
- Click any photo for a lightbox view with full metadata (GPS, thermal readings, filename)
- Auto-refreshes every 10 seconds
- Download links for each image

---

## How Detection Works

```
Pi Camera → capture_array() → every 6th frame → YOLO inference
                                                      ↓
                                              Person detected?
                                                  ↓       ↓
                                                Yes       No → keep scanning
                                                  ↓
                                        Assign ID (P1, P2...)
                                        Save detection photo + thermal + GPS
                                                  ↓
                                        Person in center drop zone?
                                                  ↓
                                        Hold for 3 seconds → LOCK ON
                                                  ↓
                                    MANUAL: wait for operator
                                    AUTO: fire immediately
                                                  ↓
                                        drop_sequence() → servos open → close
                                        Save drop photo + thermal + GPS
```

**Person ID persistence:** Each person gets a unique ID for the session. IDs persist across detections using IoU (Intersection over Union) overlap matching between frames. Stale tracks (not seen for 2 seconds) are removed. Tap **NEW MISSION** to reset all IDs back to P1.

---

## Capture File Format

Every detection and drop event saves two files:

**Photo:** `P{id}_{tag}_{timestamp}.jpg`
- `det` = detection (first time person was spotted)
- `drp` = drop (payload was released)

**JSON sidecar:** same filename, `.json` extension

```json
{
  "file": "P1_det_20260215_143012.jpg",
  "person_id": 1,
  "label": "P1",
  "timestamp": "2026-02-15 14:30:12",
  "event": "detection",
  "gps_lat": 38.8315234,
  "gps_lon": -77.3071456,
  "gps_alt": 82.4,
  "thermo_max_c": 36.8,
  "thermo_mean_c": 29.3
}
```

---

## Hardware Wiring Reference

### MLX90640 Thermal Camera (I2C)
| MLX90640 Pin | Pi Pin |
|---|---|
| VIN | 3.3V (Pin 1) |
| GND | GND (Pin 6) |
| SDA | GPIO 2 / SDA (Pin 3) |
| SCL | GPIO 3 / SCL (Pin 5) |

### NEO-6M GPS (UART Serial → `/dev/ttyUSB0`)
Connect via USB-to-UART adapter, or direct UART:
| NEO-6M Pin | Pi Pin |
|---|---|
| VCC | 3.3V (Pin 1) |
| GND | GND (Pin 6) |
| TX | GPIO 15 / RXD (Pin 10) |
| RX | GPIO 14 / TXD (Pin 8) |

> If using direct UART, change `GPS_PORT = "/dev/ttyAMA0"` in `app.py`.

### Servo Motors (GPIO PWM)
| Servo | GPIO Pin | Physical Pin |
|---|---|---|
| Servo A | GPIO 18 | Pin 12 |
| Servo B | GPIO 23 | Pin 16 |

> Power servo VCC and GND from a separate 5V supply rail — do not power servos from the Pi's GPIO 5V pin under full load.

---

## Configuration

All tunable parameters are at the top of `app.py`:

```python
LOCK_ON_SECONDS = 3.0      # How long person must stay in zone before lock
CONFIDENCE_MIN  = 0.45     # Minimum YOLO confidence to count as a detection
GPS_PORT        = "/dev/ttyUSB0"   # Serial port for NEO-6M GPS
GPS_BAUD        = 9600
```

Drop angles are in `dropper.py`:
```python
ANGLES = {
    "A": {"HOLD": 20, "DROP": 160},
    "B": {"HOLD": 20, "DROP": 160},
}
```

---

## Campus / FAA Note

This project was developed at George Mason University, which falls under FAA airspace restrictions near Washington, D.C. (GMU Policy 1414 prohibits drone flights on campus). All live flight testing was conducted at off-campus locations. The hackathon demo uses the drone secured to a static CNC-machined test stand — the full system runs and can be controlled remotely, but the vehicle does not fly.

FAA TRUST certification was obtained for any off-campus test flights.

---

## Known Limitations

- Person re-identification is IoU-based only — if someone leaves and re-enters frame they get a new ID
- Thermal heatmap is saved as a separate PNG (not overlaid on the RGB feed)
- GPS fix takes 30–90 seconds outdoors on cold start
- Servo jitter warning on startup is expected — system uses software PWM; add pigpio for smoother operation

---

## License

MIT
