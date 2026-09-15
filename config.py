# config.py
# ------------------------------------------------------------------
# All tunable constants for the Employee Presence & Idle-Time Monitor.
# Edit values here to change app behaviour without touching other files.
# ------------------------------------------------------------------

import os

# ── Camera ────────────────────────────────────────────────────────
CAMERA_INDEX   = 0          # Webcam index (0 = default)
WINDOW_NAME    = "Employee Presence Monitor  |  Press Q to quit"

# ── State machine ─────────────────────────────────────────────────
GRACE_PERIOD_SEC = 5.0      # Seconds before PRESENT → AWAY transition

# States
STATE_PRESENT = "PRESENT"
STATE_AWAY    = "AWAY"

# ── Face detection ────────────────────────────────────────────────
MIN_FACE_SIZE  = (60, 60)   # Minimum face size (w, h) — used by Haar fallback
DNN_CONFIDENCE = 0.65       # Minimum confidence for DNN detections (0.0–1.0)

# DNN model paths (saved next to this file on first run)
_BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
DNN_PROTO_PATH = os.path.join(_BASE_DIR, "deploy.prototxt")
DNN_MODEL_PATH = os.path.join(_BASE_DIR, "res10_300x300_ssd_iter_140000.caffemodel")

# DNN model download URLs (OpenCV's pretrained ResNet-SSD face detector)
DNN_PROTO_URL  = (
    "https://raw.githubusercontent.com/opencv/opencv/master/"
    "samples/dnn/face_detector/deploy.prototxt"
)
DNN_MODEL_URL  = (
    "https://github.com/opencv/opencv_3rdparty/raw/"
    "dnn_samples_face_detector_20170830/"
    "res10_300x300_ssd_iter_140000.caffemodel"
)

# ── Colour palette (BGR) ──────────────────────────────────────────
COLOR_PRESENT   = (50,  205, 50)   # Lime-green  — face present
COLOR_AWAY      = (60,  60,  220)  # Vivid red   — face away
COLOR_TEXT_MAIN = (255, 255, 255)  # White
COLOR_BG_DARK   = (20,  20,  20)   # Near-black HUD panel background
