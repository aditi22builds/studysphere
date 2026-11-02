"""
==============================================================================
StudySphere — Focus Timer Module
==============================================================================
Author: Senior Python Mentor & Architect
Role: State machine for Pomodoro study intervals. Handles session timing,
      state transitions (Focus, Short Break, Long Break), and persists
      completed study logs to SQLite without blocking the GUI event loop.

Python Concepts Used:
- State Machine design pattern
- Event callbacks for decoupling business logic from UI rendering
- Datetime calculations for historical study statistics
"""

from datetime import datetime, date, timedelta
from database.db_manager import DatabaseManager


class FocusTimer:
    """
    Manages study session intervals and state transitions.
    Designed to work with Tkinter's non-blocking `after()` timer loop.
    """

    # Default Pomodoro durations in seconds
    FOCUS_DURATION = 25 * 60       # 25 minutes
    SHORT_BREAK_DURATION = 5 * 60   # 5 minutes
    LONG_BREAK_DURATION = 15 * 60  # 15 minutes

    STATE_IDLE = "IDLE"
    STATE_RUNNING = "RUNNING"
    STATE_PAUSED = "PAUSED"
    STATE_COMPLETED = "COMPLETED"

    TYPE_FOCUS = "Focus"
    TYPE_SHORT_BREAK = "Short Break"
    TYPE_LONG_BREAK = "Long Break"

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

        self.current_type = self.TYPE_FOCUS
        self.total_seconds = self.FOCUS_DURATION
        self.remaining_seconds = self.FOCUS_DURATION
        self.state = self.STATE_IDLE
        self.active_subject_id = None
        self.session_notes = ""

        # Callbacks (provided by UI controller)
        self.on_tick_callback = None
        self.on_complete_callback = None

    def set_session_type(self, session_type: str, custom_minutes: int = None) -> None:
        """
        Switches the timer mode and resets the countdown.
        """
        self.current_type = session_type
        self.state = self.STATE_IDLE

        if custom_minutes and custom_minutes > 0:
            self.total_seconds = custom_minutes * 60
        elif session_type == self.TYPE_SHORT_BREAK:
            self.total_seconds = self.SHORT_BREAK_DURATION
        elif session_type == self.TYPE_LONG_BREAK:
            self.total_seconds = self.LONG_BREAK_DURATION
        else:
            self.total_seconds = self.FOCUS_DURATION

        self.remaining_seconds = self.total_seconds

    def start(self) -> None:
        """Starts or resumes the countdown."""
        if self.state in (self.STATE_IDLE, self.STATE_PAUSED):
            self.state = self.STATE_RUNNING

    def pause(self) -> None:
        """Pauses the active countdown."""
        if self.state == self.STATE_RUNNING:
            self.state = self.STATE_PAUSED

    def reset(self) -> None:
        """Resets the timer back to the start of the current session type."""
        self.state = self.STATE_IDLE
        self.remaining_seconds = self.total_seconds

    def tick(self) -> bool:
        """
        Decrements the timer by 1 second.
        Called once every second by the UI's non-blocking after() scheduler.
        
        Returns:
            True if session just completed, False otherwise.
        """
        if self.state != self.STATE_RUNNING:
            return False

        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1

        if self.remaining_seconds <= 0:
            self.state = self.STATE_COMPLETED
            self._record_completed_session()
            if self.on_complete_callback:
                self.on_complete_callback(self.current_type)
            return True

        if self.on_tick_callback:
            self.on_tick_callback(self.remaining_seconds, self.get_progress_ratio())

        return False

    def get_progress_ratio(self) -> float:
        """
        Returns a float between 0.0 and 1.0 indicating completion progress.
        """
        if self.total_seconds <= 0:
            return 1.0
        elapsed = self.total_seconds - self.remaining_seconds
        return min(1.0, max(0.0, elapsed / self.total_seconds))

    def get_formatted_time(self) -> str:
        """
        Returns current remaining time formatted as MM:SS.
        """
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def _record_completed_session(self) -> int:
        """
        Saves the completed study interval to the SQLite database.
        """
        duration_minutes = round(self.total_seconds / 60.0, 1)
        sql = """
            INSERT INTO study_sessions (subject_id, duration_minutes, session_type, notes, completed_at)
            VALUES (?, ?, ?, ?, ?)
        """
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        session_id = self.db.execute_insert(
            sql,
            (self.active_subject_id, duration_minutes, self.current_type, self.session_notes, now_str)
        )
        return session_id

    # --------------------------------------------------------------------------
    # Study Statistics Helpers
    # --------------------------------------------------------------------------
    def get_today_study_minutes(self) -> float:
        """Returns total minutes studied today during 'Focus' sessions."""
        today_start = date.today().isoformat() + " 00:00:00"
        sql = """
            SELECT COALESCE(SUM(duration_minutes), 0.0) AS total_min
            FROM study_sessions
            WHERE session_type = 'Focus' AND completed_at >= ?
        """
        row = self.db.fetch_one(sql, (today_start,))
        return float(row["total_min"]) if row else 0.0

    def get_total_study_hours(self) -> float:
        """Returns cumulative focus hours logged across all time."""
        sql = """
            SELECT COALESCE(SUM(duration_minutes), 0.0) AS total_min
            FROM study_sessions
            WHERE session_type = 'Focus'
        """
        row = self.db.fetch_one(sql)
        total_min = float(row["total_min"]) if row else 0.0
        return round(total_min / 60.0, 1)

    def get_recent_sessions(self, limit: int = 10) -> list[dict]:
        """Returns the most recent completed study sessions."""
        sql = """
            SELECT ss.*, s.name AS subject_name, s.code AS subject_code, s.color AS subject_color
            FROM study_sessions ss
            LEFT JOIN subjects s ON ss.subject_id = s.id
            ORDER BY ss.completed_at DESC
            LIMIT ?
        """
        return self.db.fetch_all(sql, (limit,))
