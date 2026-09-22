# logger.py
# ------------------------------------------------------------------
# CSV-based presence logging for Employee Presence & Idle-Time Monitor.
# Logs every state change and session summary to a CSV file.
# ------------------------------------------------------------------

import csv
import os
import time
from datetime import datetime, timezone


class PresenceLogger:
    """
    Logs presence state transitions and session events to a CSV file.

    CSV columns:
        timestamp          — ISO 8601 UTC timestamp
        state              — PRESENT or AWAY
        session_duration_sec — seconds in current session
        total_present_sec  — cumulative presence time
        event              — state_change | session_start | session_end | tick
    """

    FILENAME = "presence_log.csv"

    def __init__(self, base_dir: str | None = None) -> None:
        if base_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        self.path = os.path.join(base_dir, self.FILENAME)
        self._last_logged_state: str | None = None
        self._opened = False

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------

    def log_state_change(
        self,
        state: str,
        session_duration_sec: float,
        total_present_sec: float,
    ) -> None:
        """Log a state transition."""
        if state == self._last_logged_state:
            return  # avoid duplicate rows for the same state
        self._write_row(
            state=state,
            session_duration_sec=session_duration_sec,
            total_present_sec=total_present_sec,
            event="state_change",
        )
        self._last_logged_state = state

    def log_session_end(self, total_present_sec: float) -> None:
        """Log the final session summary when the program exits."""
        self._write_row(
            state="END",
            session_duration_sec=0.0,
            total_present_sec=total_present_sec,
            event="session_end",
        )

    def log_tick(
        self,
        state: str,
        session_duration_sec: float,
        total_present_sec: float,
    ) -> None:
        """
        Periodic tick log (optional, can be called every N seconds).
        Disabled by default to avoid flooding the CSV.
        """
        # Uncomment to enable periodic logging every tick:
        # self._write_row(state, session_duration_sec, total_present_sec, "tick")
        pass

    # ------------------------------------------------------------------
    #  Internal
    # ------------------------------------------------------------------

    def _write_row(
        self,
        state: str,
        session_duration_sec: float,
        total_present_sec: float,
        event: str,
    ) -> None:
        timestamp = datetime.now(timezone.utc).isoformat()
        file_exists = os.path.isfile(self.path)
        with open(self.path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(
                    [
                        "timestamp",
                        "state",
                        "session_duration_sec",
                        "total_present_sec",
                        "event",
                    ]
                )
            writer.writerow(
                [
                    timestamp,
                    state,
                    f"{session_duration_sec:.2f}",
                    f"{total_present_sec:.2f}",
                    event,
                ]
            )
        self._opened = True

    def ensure_file_exists(self) -> None:
        """Create the CSV file with headers if it does not exist."""
        if not self._opened and not os.path.isfile(self.path):
            with open(self.path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "timestamp",
                        "state",
                        "session_duration_sec",
                        "total_present_sec",
                        "event",
                    ]
                )
            self._opened = True
