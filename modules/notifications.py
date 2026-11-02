"""
==============================================================================
StudySphere — Notifications & Reminders Module
==============================================================================
Author: Senior Python Mentor & Architect
Role: Automatically evaluates task deadlines, overdue assignments, and daily
      study milestones, generating categorized real-time alerts.

Python Concepts Used:
- Datetime delta comparisons
- Categorized data structures (Dictionaries / Dataclasses)
- Threshold-based event triggers
"""

from datetime import datetime, date, timedelta
from database.db_manager import DatabaseManager


class NotificationManager:
    """
    Evaluates database state and produces categorized academic notifications.
    """

    SEV_CRITICAL = "CRITICAL" # Overdue assignments
    SEV_WARNING = "WARNING"   # Due within 48 hours
    SEV_INFO = "INFO"         # Study goal reminders & achievements

    DAILY_STUDY_GOAL_MINUTES = 120 # 2 hours study goal for CS students

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def get_all_notifications(self) -> list[dict]:
        """
        Scans tasks and study sessions to build a complete list of active notifications.
        """
        notifications = []
        today = date.today()
        today_str = today.isoformat()
        tomorrow_str = (today + timedelta(days=1)).isoformat()
        two_days_str = (today + timedelta(days=2)).isoformat()

        # 1. Check Overdue Tasks
        sql_overdue = """
            SELECT t.id, t.title, t.due_date, s.name AS subject_name, s.color AS subject_color
            FROM tasks t
            LEFT JOIN subjects s ON t.subject_id = s.id
            WHERE t.status != 'Completed' AND t.due_date < ?
            ORDER BY t.due_date ASC
        """
        overdue_tasks = self.db.fetch_all(sql_overdue, (today_str,))
        for t in overdue_tasks:
            try:
                task_date = datetime.strptime(t["due_date"], "%Y-%m-%d").date()
                days = (today - task_date).days
            except ValueError:
                days = 1

            notifications.append({
                "type": "overdue",
                "severity": self.SEV_CRITICAL,
                "title": f"Overdue Assignment: {t['title']}",
                "message": f"Due {days} day{'s' if days > 1 else ''} ago ({t['due_date']}). Subject: {t['subject_name'] or 'General'}",
                "timestamp": t["due_date"],
                "color": "#EF4444", # Rose red
                "task_id": t["id"]
            })

        # 2. Check Tasks Due Today or Tomorrow
        sql_upcoming = """
            SELECT t.id, t.title, t.due_date, s.name AS subject_name, s.color AS subject_color
            FROM tasks t
            LEFT JOIN subjects s ON t.subject_id = s.id
            WHERE t.status != 'Completed' AND t.due_date >= ? AND t.due_date <= ?
            ORDER BY t.due_date ASC
        """
        upcoming_tasks = self.db.fetch_all(sql_upcoming, (today_str, two_days_str))
        for t in upcoming_tasks:
            is_today = (t["due_date"] == today_str)
            label = "TODAY" if is_today else "TOMORROW"
            notifications.append({
                "type": "deadline",
                "severity": self.SEV_WARNING if is_today else self.SEV_INFO,
                "title": f"Upcoming Deadline: {t['title']}",
                "message": f"Due {label} ({t['due_date']}) for {t['subject_name'] or 'General'}.",
                "timestamp": t["due_date"],
                "color": "#F59E0B" if is_today else "#3B82F6", # Amber or Blue
                "task_id": t["id"]
            })

        # 3. Check Daily Study Goal Progress
        today_start = today_str + " 00:00:00"
        sql_study = """
            SELECT COALESCE(SUM(duration_minutes), 0.0) AS total_today
            FROM study_sessions
            WHERE session_type = 'Focus' AND completed_at >= ?
        """
        study_row = self.db.fetch_one(sql_study, (today_start,))
        studied_minutes = float(study_row["total_today"]) if study_row else 0.0

        if studied_minutes >= self.DAILY_STUDY_GOAL_MINUTES:
            notifications.append({
                "type": "goal_achieved",
                "severity": self.SEV_INFO,
                "title": "🎉 Daily Study Goal Achieved!",
                "message": f"Outstanding! You've logged {studied_minutes:.0f} mins of focus time today (Goal: {self.DAILY_STUDY_GOAL_MINUTES} mins).",
                "timestamp": today_str,
                "color": "#10B981", # Emerald
                "task_id": None
            })
        else:
            remaining = self.DAILY_STUDY_GOAL_MINUTES - studied_minutes
            notifications.append({
                "type": "goal_reminder",
                "severity": self.SEV_INFO,
                "title": "Daily Focus Goal",
                "message": f"You've completed {studied_minutes:.0f} of {self.DAILY_STUDY_GOAL_MINUTES} mins today. {remaining:.0f} mins remaining to hit your target!",
                "timestamp": today_str,
                "color": "#8B5CF6", # Violet
                "task_id": None
            })

        return notifications

    def get_notification_counts(self) -> dict:
        """
        Returns summary count of notifications partitioned by severity.
        """
        all_notifs = self.get_all_notifications()
        critical = sum(1 for n in all_notifs if n["severity"] == self.SEV_CRITICAL)
        warning = sum(1 for n in all_notifs if n["severity"] == self.SEV_WARNING)
        info = sum(1 for n in all_notifs if n["severity"] == self.SEV_INFO)

        return {
            "total": len(all_notifs),
            "critical": critical,
            "warning": warning,
            "info": info,
            "badge_count": critical + warning # Actionable items
        }
