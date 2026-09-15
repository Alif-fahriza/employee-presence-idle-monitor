# detector.py
# ------------------------------------------------------------------
# Face detector loader and per-frame detection logic.
#
# Preferred detector : OpenCV DNN (ResNet-SSD) — downloaded once (~10 MB).
# Automatic fallback : Haar Cascade (always available via cv2.data).
# ------------------------------------------------------------------

import os
import urllib.request

import cv2

from config import (
    DNN_CONFIDENCE,
    DNN_MODEL_PATH, DNN_MODEL_URL,
    DNN_PROTO_PATH,  DNN_PROTO_URL,
    MIN_FACE_SIZE,
)


# ──────────────────────────────────────────────────────────────────
#  Internal helpers
# ──────────────────────────────────────────────────────────────────

def _try_download(url: str, dest: str) -> bool:
    """Download *url* to *dest*. Prints progress. Returns True on success."""
    try:
        print(f"  Downloading {os.path.basename(dest)} ...", end=" ", flush=True)
        urllib.request.urlretrieve(url, dest)
        print("OK")
        return True
    except Exception as exc:
        print(f"FAILED ({exc})")
        return False


# ──────────────────────────────────────────────────────────────────
#  Public API
# ──────────────────────────────────────────────────────────────────

def load_detector():
    """
    Load and return a face detector.

    Preference order
    ----------------
    1. OpenCV DNN (ResNet-SSD) — downloads model files on first run.
    2. Haar Cascade            — built-in fallback, no download required.

    Returns
    -------
    (detector, mode)
        detector : the loaded model object
        mode     : 'dnn' or 'haar'
    """
    # ── Try DNN ───────────────────────────────────────────────────
    proto_ok = os.path.isfile(DNN_PROTO_PATH) or _try_download(DNN_PROTO_URL, DNN_PROTO_PATH)
    model_ok = os.path.isfile(DNN_MODEL_PATH) or _try_download(DNN_MODEL_URL, DNN_MODEL_PATH)

    if proto_ok and model_ok:
        try:
            net = cv2.dnn.readNetFromCaffe(DNN_PROTO_PATH, DNN_MODEL_PATH)
            print("[Detector] Using ResNet-SSD DNN face detector.")
            return net, "dnn"
        except Exception as exc:
            print(f"[Detector] DNN load failed: {exc}. Falling back to Haar.")

    # ── Fallback: Haar Cascade ────────────────────────────────────
    haar_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    cascade = cv2.CascadeClassifier(haar_path)
    if cascade.empty():
        raise RuntimeError(
            "Haar Cascade model not found. OpenCV installation may be broken."
        )
    print("[Detector] Using Haar Cascade face detector (fallback).")
    return cascade, "haar"


def detect_face(frame, detector, mode: str):
    """
    Run face detection on a single *frame*.

    Parameters
    ----------
    frame    : BGR numpy array (from cv2.VideoCapture.read)
    detector : object returned by load_detector()
    mode     : 'dnn' or 'haar'

    Returns
    -------
    (x, y, w, h) bounding box of the best detected face,
    or None if no face is found.
    """
    h, w = frame.shape[:2]

    if mode == "dnn":
        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)), 1.0,
            (300, 300), (104.0, 177.0, 123.0),
        )
        detector.setInput(blob)
        detections = detector.forward()

        best_box  = None
        best_conf = DNN_CONFIDENCE   # accept only detections above threshold

        for i in range(detections.shape[2]):
            confidence = float(detections[0, 0, i, 2])
            if confidence >= best_conf:
                box = detections[0, 0, i, 3:7] * [w, h, w, h]
                x1, y1, x2, y2 = box.astype(int)
                # Clamp to frame boundaries
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w - 1, x2), min(h - 1, y2)
                if x2 > x1 and y2 > y1:
                    best_box  = (x1, y1, x2 - x1, y2 - y1)
                    best_conf = confidence   # keep the most-confident detection
        return best_box

    else:  # haar
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        faces = detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=MIN_FACE_SIZE,
            flags=cv2.CASCADE_SCALE_IMAGE,
        )
        if len(faces) == 0:
            return None
        # Return the largest face by area
        return max(faces, key=lambda f: f[2] * f[3])
