"""
Employee Presence & Idle-Time Monitor
======================================
Usage:
    python main.py

Description:
    Opens the default webcam and detects whether an employee is present
    (face visible) or away (face missing). Overlays real-time status,
    a per-session timer, and cumulative presence time on the video feed.

Controls:
    Press 'q' to quit. Total presence time is printed to the console on exit.

Dependencies:
    pip install opencv-python

Project structure:
    main.py      ← entry point (this file)
    config.py    ← all tunable constants
    detector.py  ← face detector loading & per-frame detection
    hud.py       ← on-screen overlay drawing
"""

import time

import cv2

from config import (
    CAMERA_INDEX,
    FR_RECOGNIZE_COOLDOWN,
    GRACE_PERIOD_SEC,
    STATE_AWAY,
    STATE_PRESENT,
    WINDOW_NAME,
)
from detector import detect_face, load_detector
from hud import draw_hud, fmt_duration
from recognizer import FaceRecognizer


def main() -> None:
    print("=" * 54)
    print("  Employee Presence & Idle-Time Monitor")
    print("  Press Q in the video window to quit.")
    print("=" * 54)

    # ── Load face detector ─────────────────────────────────────────
    detector, mode = load_detector()

    # ── Initialise face recogniser ─────────────────────────────────
    recogniser = FaceRecognizer()

    # ── Open webcam ────────────────────────────────────────────────
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera index {CAMERA_INDEX}.")
    print(f"[Camera] Opened camera index {CAMERA_INDEX}.")

    # ── State machine variables ────────────────────────────────────
    state              = STATE_AWAY      # Start: assume nobody in frame
    state_start_time   = time.monotonic()
    last_face_time     = None            # Monotonic timestamp of last detection
    total_present_secs = 0.0             # Cumulative time spent in PRESENT
    last_tick          = time.monotonic()

    # Recogniser throttle: do not run predict every single frame
    last_recog_time  = 0.0               # Monotonic timestamp of last recognition
    known_name       = None              # Last recognised name
    known_confidence = None              # Last confidence value

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[Warning] Failed to read frame — skipping.")
                time.sleep(0.05)
                continue

            now      = time.monotonic()
            dt       = now - last_tick   # seconds elapsed since last frame
            last_tick = now

            # ── Face detection ─────────────────────────────────────
            face_box   = detect_face(frame, detector, mode)
            face_found = face_box is not None

            if face_found:
                last_face_time = now   # record last-seen timestamp

            # ── Face recognition (throttled) ───────────────────────
            if face_found and (now - last_recog_time) >= FR_RECOGNIZE_COOLDOWN:
                x, y, w, h = face_box
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                face_roi = gray[y : y + h, x : x + w]
                if face_roi.size > 0:
                    name, conf = recogniser.identify(face_roi)
                    known_name       = name
                    known_confidence = conf
                last_recog_time = now

            elif not face_found:
                known_name       = None
                known_confidence = None

            # ── State transitions ──────────────────────────────────
            time_since_face = (
                (now - last_face_time) if last_face_time is not None else float("inf")
            )

            if state == STATE_AWAY:
                if face_found:
                    # Immediately switch to PRESENT on detection
                    state            = STATE_PRESENT
                    state_start_time = now

            elif state == STATE_PRESENT:
                if not face_found and time_since_face >= GRACE_PERIOD_SEC:
                    # Leave PRESENT only after grace period expires
                    state            = STATE_AWAY
                    state_start_time = now

            # ── Accumulate presence time ───────────────────────────
            if state == STATE_PRESENT:
                total_present_secs += dt

            # ── Compute display values ─────────────────────────────
            session_secs = now - state_start_time

            # Grace countdown: only relevant while in PRESENT with face missing
            grace_remaining = 0.0
            if state == STATE_PRESENT and not face_found and last_face_time is not None:
                grace_remaining = max(0.0, GRACE_PERIOD_SEC - time_since_face)

            # ── Render & display ───────────────────────────────────
            draw_hud(frame, state, session_secs, total_present_secs,
                     face_box, grace_remaining, known_name, known_confidence)
            cv2.imshow(WINDOW_NAME, frame)

            # ── Quit on 'q' ────────────────────────────────────────
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()

    # ── Exit summary ───────────────────────────────────────────────
    print()
    print("=" * 54)
    print("  Session ended.")
    print(f"  Total presence time : {fmt_duration(total_present_secs)}")
    print("=" * 54)


if __name__ == "__main__":
    main()
