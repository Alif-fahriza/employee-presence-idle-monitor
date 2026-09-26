# hud.py
# ------------------------------------------------------------------
# All on-screen drawing / overlay logic for the presence monitor.
# ------------------------------------------------------------------

import datetime

import cv2

from config import (
    COLOR_AWAY, COLOR_BG_DARK, COLOR_PRESENT, COLOR_TEXT_MAIN,
    COLOR_UNKNOWN, SHOW_NAME_OVERLAY, STATE_PRESENT,
)


# ──────────────────────────────────────────────────────────────────
#  Utility
# ──────────────────────────────────────────────────────────────────

def fmt_duration(seconds: float) -> str:
    """Format *seconds* as a HH:MM:SS string."""
    seconds = max(0, int(seconds))
    h, rem = divmod(seconds, 3600)
    m, s   = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


# ──────────────────────────────────────────────────────────────────
#  HUD renderer
# ──────────────────────────────────────────────────────────────────

def draw_hud(
    frame,
    state: str,
    session_secs: float,
    total_present_secs: float,
    face_box,
    grace_remaining: float,
    known_name: str | None = None,
    known_confidence: float | None = None,
) -> None:
    """
    Render the full HUD overlay onto *frame* in-place.

    Draws
    -----
    - Face bounding box with label, recognition name & total presence badge
    - Real-time wall clock at top-right corner
    - Semi-transparent status panel at the bottom
    - Status badge (PRESENT / AWAY)
    - Session timer and cumulative presence time
    - Grace period countdown (when applicable)
    - Recognised employee name & confidence (when available)
    """
    fh, fw = frame.shape[:2]
    color  = COLOR_PRESENT if state == STATE_PRESENT else COLOR_AWAY
    panel_h = 90

    # ── Face bounding box + total presence badge ──────────────────
    if face_box is not None:
        x, y, bw, bh = face_box

        # Bounding rectangle
        cv2.rectangle(frame, (x, y), (x + bw, y + bh), color, 2)

        # Label above the box
        if SHOW_NAME_OVERLAY and known_name:
            lbl_text = f"{known_name} ({known_confidence})" if known_confidence else known_name
        else:
            lbl_text = "Face detected"
        (lw, lh), _ = cv2.getTextSize(lbl_text, cv2.FONT_HERSHEY_DUPLEX, 0.52, 1)
        lbl_y = max(y - 8, lh + 8)
        lbl_x = max(6, min(fw - lw - 6, x))
        cv2.rectangle(
            frame,
            (lbl_x - 4, lbl_y - lh - 4),
            (lbl_x + lw + 4, lbl_y + 4),
            (0, 0, 0), -1,
        )
        cv2.rectangle(
            frame,
            (lbl_x - 4, lbl_y - lh - 4),
            (lbl_x + lw + 4, lbl_y + 4),
            color, 1,
        )
        cv2.putText(frame, lbl_text, (lbl_x, lbl_y),
                    cv2.FONT_HERSHEY_DUPLEX, 0.52, color, 1, cv2.LINE_AA)

        # Total presence badge attached to the bounding box
        pres_str = f"Total Presence: {fmt_duration(total_present_secs)}"
        (pres_w, pres_h), _ = cv2.getTextSize(
            pres_str, cv2.FONT_HERSHEY_DUPLEX, 0.52, 1
        )
        pres_x = max(6, min(fw - pres_w - 6, x + (bw - pres_w) // 2))

        # Position below the box if space allows, otherwise inside bottom edge
        if (y + bh + pres_h + 16) <= (fh - panel_h):
            bg_top = y + bh
            bg_bot = y + bh + pres_h + 12
            pres_y = bg_bot - 6
        else:
            bg_bot = y + bh
            bg_top = y + bh - pres_h - 12
            pres_y = bg_bot - 6

        # Dark pill background with colored border
        cv2.rectangle(
            frame,
            (pres_x - 6, bg_top),
            (pres_x + pres_w + 6, bg_bot),
            (0, 0, 0), -1,
        )
        cv2.rectangle(
            frame,
            (pres_x - 6, bg_top),
            (pres_x + pres_w + 6, bg_bot),
            color, 1,
        )
        cv2.putText(frame, pres_str, (pres_x, pres_y),
                    cv2.FONT_HERSHEY_DUPLEX, 0.52, color, 1, cv2.LINE_AA)

    # ── Bottom HUD panel (semi-transparent) ───────────────────────
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, fh - panel_h), (fw, fh), COLOR_BG_DARK, -1)
    cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

    # ── Status badge ───────────────────────────────────────────────
    badge_text = f"  {state}  "
    bx, by = 10, fh - panel_h + 30
    (tw, th), _ = cv2.getTextSize(badge_text, cv2.FONT_HERSHEY_DUPLEX, 0.85, 2)
    cv2.rectangle(frame, (bx - 4, by - th - 6), (bx + tw + 4, by + 4), color, -1)
    cv2.putText(frame, badge_text, (bx, by),
                cv2.FONT_HERSHEY_DUPLEX, 0.85, (0, 0, 0), 2, cv2.LINE_AA)

    # ── Session timer ──────────────────────────────────────────────
    sess_label = "Time present:" if state == STATE_PRESENT else "Time away:"
    cv2.putText(frame, sess_label,
                (10, fh - panel_h + 58),
                cv2.FONT_HERSHEY_SIMPLEX, 0.52, (180, 180, 180), 1, cv2.LINE_AA)
    cv2.putText(frame, fmt_duration(session_secs),
                (10, fh - panel_h + 78),
                cv2.FONT_HERSHEY_DUPLEX, 0.65, color, 1, cv2.LINE_AA)

    # ── Cumulative presence time ───────────────────────────────────
    cv2.putText(frame, "Total presence:",
                (fw // 2 - 10, fh - panel_h + 58),
                cv2.FONT_HERSHEY_SIMPLEX, 0.52, (180, 180, 180), 1, cv2.LINE_AA)
    cv2.putText(frame, fmt_duration(total_present_secs),
                (fw // 2 - 10, fh - panel_h + 78),
                cv2.FONT_HERSHEY_DUPLEX, 0.65, COLOR_TEXT_MAIN, 1, cv2.LINE_AA)

    # ── Grace period countdown ─────────────────────────────────────
    if grace_remaining > 0:
        grace_msg = f"Grace: {grace_remaining:.1f}s"
        cv2.putText(frame, grace_msg,
                    (fw - 160, fh - panel_h + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (80, 180, 255), 1, cv2.LINE_AA)

    # ── Wall clock (top-right corner) ─────────────────────────────
    clock_str = datetime.datetime.now().strftime("%H:%M:%S")
    (clk_w, clk_h), _ = cv2.getTextSize(clock_str, cv2.FONT_HERSHEY_DUPLEX, 0.65, 1)
    clk_x = fw - clk_w - 18
    clk_y = 28
    cv2.rectangle(
        frame,
        (clk_x - 8, clk_y - clk_h - 6),
        (clk_x + clk_w + 8, clk_y + 6),
        (0, 0, 0), -1,
    )
    cv2.rectangle(
        frame,
        (clk_x - 8, clk_y - clk_h - 6),
        (clk_x + clk_w + 8, clk_y + 6),
        (60, 60, 60), 1,
    )
    cv2.putText(frame, clock_str, (clk_x, clk_y),
                cv2.FONT_HERSHEY_DUPLEX, 0.65, COLOR_TEXT_MAIN, 1, cv2.LINE_AA)
