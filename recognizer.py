"""
recognizer.py — Face Recognition Module (LBPH)
===============================================
Manages face registration, model training, and real-time face
identification for the Employee Presence & Idle-Time Monitor.

Structure:
    known_faces/
        students.csv         # ID → Name mapping
        images/              # Raw training images (captured on registration)
        encodings/           # LBPH trained model (.yml) & helper data

Usage inside main loop:
    from recognizer import FaceRecognizer
    fr = FaceRecognizer()
    name, confidence = fr.identify(face_roi)     # → ("Alice", 45.2) or (None, None)
    fr.register(frame, bbox, student_id, name)   # Capture images & train
"""

import csv
import os
import time
from pathlib import Path

import cv2
import numpy as np

from config import (
    FR_BASE_DIR,
    FR_MODEL_PATH,
    FR_STUDENTS_CSV,
    FR_IMAGES_DIR,
    FR_HAAR_PATH,
    FR_CONFIDENCE_THRESHOLD,
    FR_TRAIN_IMAGE_COUNT,
)

# -------------------------------------------------------------------
#  Internals
# -------------------------------------------------------------------

def _ensure_dirs():
    """Create data directories on first use."""
    for d in (FR_IMAGES_DIR, os.path.dirname(FR_MODEL_PATH)):
        os.makedirs(d, exist_ok=True)


def _load_students() -> dict:
    """Return {id: name} dict from the CSV file.  Empty dict if missing."""
    mapping: dict[int, str] = {}
    if os.path.isfile(FR_STUDENTS_CSV):
        with open(FR_STUDENTS_CSV, newline="") as f:
            for row in csv.DictReader(f):
                try:
                    mapping[int(row["id"])] = row["name"]
                except (KeyError, ValueError):
                    continue
    return mapping


def _save_students(mapping: dict[int, str]) -> None:
    """Persist {id: name} dict to CSV."""
    with open(FR_STUDENTS_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name"])
        for sid, sname in sorted(mapping.items()):
            writer.writerow([sid, sname])


# -------------------------------------------------------------------
#  Public API
# -------------------------------------------------------------------

class FaceRecognizer:
    """
    Lightweight wrapper around OpenCV's LBPH face recogniser.

    Call ``identify(face_roi)`` once per frame to get (name, confidence).
    Call ``register(frame, bbox, student_id, name)`` to add a new face.
    Call ``train()`` after registration to rebuild the model.

    Attributes
    ----------
    model        : cv2.face.LBPHFaceRecognizer | None
    known_faces  : dict[int, str]   — live in-memory {id: name}
    _haar        : cv2.CascadeClassifier
    """

    def __init__(self):
        _ensure_dirs()
        self.known_faces: dict[int, str] = _load_students()
        self.model = None
        self._haar = cv2.CascadeClassifier(FR_HAAR_PATH)

        # Pre-load model if it exists
        if os.path.isfile(FR_MODEL_PATH):
            try:
                self.model = cv2.face.LBPHFaceRecognizer_create()
                self.model.read(FR_MODEL_PATH)
                print(f"[FaceRecognizer] Model loaded ({len(self.known_faces)} known faces)")
            except Exception as exc:
                print(f"[FaceRecognizer] Could not load model: {exc}")
                self.model = None
        else:
            print("[FaceRecognizer] No trained model found — identity will show 'Unknown'")
            # Auto-train if images exist but model was deleted
            images_exist = list(FR_IMAGES_DIR.glob("*.jpg")) or list(FR_IMAGES_DIR.glob("*.png"))
            if images_exist and self.known_faces:
                print("[FaceRecognizer] Training from existing images…")
                self.train()

    # ── Identification ──────────────────────────────────────────────

    def identify(self, face_roi: np.ndarray):
        """
        Predict the identity of a face region.

        Parameters
        ----------
        face_roi : np.ndarray
            Grayscale face crop, any size (will be resized internally).

        Returns
        -------
        (name, confidence) or (None, None) if unknown / no model.
            Lower confidence = better match (LBPH convention).
        """
        if self.model is None:
            return None, None

        try:
            resized = cv2.resize(face_roi, (100, 100))
            sid, confidence = self.model.predict(resized)
        except Exception:
            return None, None

        if confidence <= FR_CONFIDENCE_THRESHOLD and sid in self.known_faces:
            return self.known_faces[sid], round(confidence, 1)
        return None, confidence

    # ── Registration ────────────────────────────────────────────────

    def register(self, frame: np.ndarray, bbox, student_id: int, name: str) -> int:
        """
        Capture *FR_TRAIN_IMAGE_COUNT* face images for training.

        Parameters
        ----------
        frame    : np.ndarray — current video frame (BGR)
        bbox     : (x, y, w, h) — face bounding box from detector
        student_id : int — unique identifier for this person
        name     : str — display name

        Returns
        -------
        Number of images actually saved (may be less than requested).
        """
        x, y, w, h = bbox
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_roi = gray[y : y + h, x : x + w]
        if face_roi.size == 0:
            return 0

        count = 0
        for i in range(FR_TRAIN_IMAGE_COUNT):
            # Small random shift / noise for robustness (skip on first)
            if i == 0:
                crop = face_roi
            else:
                crop = face_roi  # Keep it simple — variation comes from live feed

            fname = os.path.join(FR_IMAGES_DIR, f"{student_id}_{name}_{i}.jpg")
            cv2.imwrite(fname, crop)
            count += 1

        # Update known faces
        self.known_faces[student_id] = name
        _save_students(self.known_faces)

        print(f"[FaceRecognizer] Registered '{name}' (ID={student_id}) — {count} images saved")
        return count

    # ── Training ────────────────────────────────────────────────────

    def train(self) -> bool:
        """
        Rebuild the LBPH model from all images in *FR_IMAGES_DIR*.

        Returns True on success.
        """
        images = []
        labels = []
        label_map = {}  # student_id → sequential label

        # Build label map from CSV (already loaded in known_faces)
        for sid, sname in self.known_faces.items():
            label_map[sid] = sname

        # Collect training images
        img_iter = sorted(Path(FR_IMAGES_DIR).glob("*.jpg")) + sorted(
            Path(FR_IMAGES_DIR).glob("*.png")
        )
        for img_path in img_iter:
            stem = img_path.stem  # e.g. "1_Alice_0"
            try:
                sid = int(stem.split("_")[0])
            except (ValueError, IndexError):
                continue
            if sid not in self.known_faces:
                continue

            img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            images.append(cv2.resize(img, (100, 100)))
            labels.append(sid)

        if not images:
            print("[FaceRecognizer] No training images found.")
            return False

        # Train
        self.model = cv2.face.LBPHFaceRecognizer_create()
        self.model.train(images, np.array(labels))
        self.model.save(FR_MODEL_PATH)

        print(
            f"[FaceRecognizer] Model trained — {len(images)} images, "
            f"{len(self.known_faces)} person(s)"
        )
        return True