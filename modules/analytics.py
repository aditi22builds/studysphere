"""
==============================================================================
StudySphere — Analytics & Data Science Module
==============================================================================
Author: Senior Python Mentor & Architect
Role: Extracts relational study and task data, executes statistical calculations
      via NumPy, and renders publication-ready dark-theme Matplotlib figures.

Python Concepts Used:
- NumPy vector operations: `np.array`, `np.mean`, `np.median`, `np.std`, `np.sum`, `np.polyfit`
- Matplotlib Figure generation, custom dark styling, spines, subplots, and layouts
- Datetime date-range generation and zero-filling time series
"""

import numpy as np
import matplotlib
# Use non-interactive Agg backend to avoid standalone window popping before canvas embed
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from datetime import datetime, date, timedelta
from database.db_manager import DatabaseManager


class AnalyticsEngine:
    """
    Computes statistical metrics and builds custom dark-themed charts
    for academic productivity evaluation.
    """

    # Visual Theme Palette for Charts
    BG_DARK = "#0F172A"       # Deep slate navy background
    CARD_DARK = "#1E293B"     # Slightly lighter container
    TEXT_LIGHT = "#F8FAFC"    # Off-white font
    TEXT_MUTED = "#94A3B8"    # Slate muted font
    ACCENT_PURPLE = "#8B5CF6" # Primary brand violet
    ACCENT_CYAN = "#06B6D4"   # Secondary cyan
    ACCENT_EMERALD = "#10B981"# Success green
    ACCENT_ROSE = "#F43F5E"   # Warning rose
    GRID_COLOR = "#334155"    # Subtle grid lines

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    # --------------------------------------------------------------------------
    # Statistical Calculations with NumPy
    # --------------------------------------------------------------------------
    def get_summary_statistics(self) -> dict:
        """
        Computes descriptive statistics on study sessions and tasks using NumPy.
        Demonstrates practical Data Science concepts: mean, median, std dev, trend slope.
        """
        # Fetch all focus sessions
        sessions = self.db.fetch_all(
            "SELECT duration_minutes FROM study_sessions WHERE session_type = 'Focus'"
        )

        if not sessions:
            return {
                "total_hours": 0.0,
                "mean_session_min": 0.0,
                "median_session_min": 0.0,
                "std_session_min": 0.0,
                "consistency_score": 0.0,
                "active_days": 0,
                "trend_direction": "Neutral",
            }

        durations = np.array([s["duration_minutes"] for s in sessions], dtype=np.float64)

        total_hours = float(np.sum(durations) / 60.0)
        mean_min = float(np.mean(durations))
        median_min = float(np.median(durations))
        std_min = float(np.std(durations))

        # Fetch last 7 days of daily totals for consistency and trend analysis
        daily_records = self.get_daily_study_hours(days=7)
        daily_vals = np.array([d["hours"] for d in daily_records], dtype=np.float64)

        # Consistency score: 100 - (CV% capped)
        cv = (np.std(daily_vals) / (np.mean(daily_vals) + 1e-5)) * 100
        consistency_score = max(0.0, min(100.0, 100.0 - cv))

        # Linear regression slope over 7 days to see if study hours are increasing
        x = np.arange(len(daily_vals))
        if len(daily_vals) > 1 and np.sum(daily_vals) > 0:
            slope, _ = np.polyfit(x, daily_vals, 1)
            if slope > 0.05:
                trend_direction = "Rising (+)"
            elif slope < -0.05:
                trend_direction = "Declining (-)"
            else:
                trend_direction = "Steady (~)"
        else:
            trend_direction = "Insufficient Data"

        active_days = int(np.count_nonzero(daily_vals > 0.0))

        return {
            "total_hours": round(total_hours, 1),
            "mean_session_min": round(mean_min, 1),
            "median_session_min": round(median_min, 1),
            "std_session_min": round(std_min, 1),
            "consistency_score": round(consistency_score, 1),
            "active_days": active_days,
            "trend_direction": trend_direction,
        }

    def get_daily_study_hours(self, days: int = 7) -> list[dict]:
        """
        Returns chronological daily focus hours for the last N days,
        ensuring zero-filling for days without recorded study sessions.
        """
        today = date.today()
        start_date = today - timedelta(days=days - 1)

        sql = """
            SELECT date(completed_at) AS session_date,
                   ROUND(SUM(duration_minutes) / 60.0, 2) AS hours
            FROM study_sessions
            WHERE session_type = 'Focus' AND date(completed_at) >= ?
            GROUP BY date(completed_at)
        """
        rows = self.db.fetch_all(sql, (start_date.isoformat(),))
        data_map = {r["session_date"]: float(r["hours"]) for r in rows}

        results = []
        for i in range(days):
            current = start_date + timedelta(days=i)
            iso_str = current.isoformat()
            day_label = current.strftime("%a %d")  # e.g., "Mon 12"
            results.append({
                "date": iso_str,
                "label": day_label,
                "hours": data_map.get(iso_str, 0.0)
            })

        return results

    def get_subject_distribution(self) -> list[dict]:
        """
        Returns total study hours partitioned by subject.
        """
        sql = """
            SELECT 
                COALESCE(s.name, 'Uncategorized') AS subject_name,
                COALESCE(s.color, '#64748B') AS color,
                ROUND(SUM(ss.duration_minutes) / 60.0, 1) AS hours
            FROM study_sessions ss
            LEFT JOIN subjects s ON ss.subject_id = s.id
            WHERE ss.session_type = 'Focus'
            GROUP BY ss.subject_id
            HAVING hours > 0
            ORDER BY hours DESC
        """
        return self.db.fetch_all(sql)

    def get_weekly_task_velocity(self) -> dict:
        """
        Computes weekly task creation vs completion numbers for trend analysis.
        """
        today = date.today()
        start_date = today - timedelta(days=28)  # Last 4 weeks

        tasks = self.db.fetch_all(
            "SELECT created_at, completed_at, status FROM tasks WHERE created_at >= ?",
            (start_date.isoformat(),)
        )
        total_created = len(tasks)
        total_completed = sum(1 for t in tasks if t["status"] == "Completed")

        return {
            "created": total_created,
            "completed": total_completed,
            "rate": round((total_completed / total_created * 100), 1) if total_created > 0 else 0.0
        }

    # --------------------------------------------------------------------------
    # Matplotlib Dark-Themed Figure Generators
    # --------------------------------------------------------------------------
    def create_daily_hours_chart(self, days: int = 7) -> Figure:
        """
        Builds a modern bar chart of daily study hours.
        """
        records = self.get_daily_study_hours(days=days)
        labels = [r["label"] for r in records]
        hours = [r["hours"] for r in records]

        fig = Figure(figsize=(6.2, 3.2), dpi=100, facecolor=self.CARD_DARK)
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.CARD_DARK)

        bars = ax.bar(labels, hours, color=self.ACCENT_PURPLE, width=0.55, edgecolor="#A78BFA", linewidth=1.2, zorder=3)

        # Highlight maximum bar
        if hours and max(hours) > 0:
            max_idx = hours.index(max(hours))
            bars[max_idx].set_color("#6366F1")
            bars[max_idx].set_edgecolor("#C084FC")

        # Styling
        ax.grid(axis="y", color=self.GRID_COLOR, linestyle="--", alpha=0.7, zorder=0)
        ax.set_ylabel("Hours Studied", color=self.TEXT_MUTED, fontsize=9, fontweight="bold")
        ax.set_title(f"Focus Time: Last {days} Days", color=self.TEXT_LIGHT, fontsize=11, fontweight="bold", pad=12)
        ax.tick_params(colors=self.TEXT_MUTED, labelsize=8)

        # Remove top and right borders
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(self.GRID_COLOR)
        ax.spines["bottom"].set_color(self.GRID_COLOR)

        # Add data values on top of bars
        for bar, h in zip(bars, hours):
            if h > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.05,
                    f"{h:.1f}h",
                    ha="center",
                    va="bottom",
                    color=self.TEXT_LIGHT,
                    fontsize=8,
                    fontweight="bold"
                )

        fig.tight_layout()
        return fig

    def create_subject_donut_chart(self) -> Figure:
        """
        Builds an elegant donut chart showing subject-wise study hour breakdown.
        """
        dist = self.get_subject_distribution()
        fig = Figure(figsize=(5.0, 3.2), dpi=100, facecolor=self.CARD_DARK)
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.CARD_DARK)

        if not dist:
            # Empty state inside chart
            ax.text(0.5, 0.5, "No focus sessions recorded yet.\nStart the Focus Timer to see distribution!",
                    ha="center", va="center", color=self.TEXT_MUTED, fontsize=9)
            ax.axis("off")
            fig.tight_layout()
            return fig

        labels = [d["subject_name"] for d in dist]
        hours = [d["hours"] for d in dist]
        colors = [d["color"] for d in dist]

        # Draw donut
        wedges, texts, autotexts = ax.pie(
            hours,
            labels=labels,
            colors=colors,
            autopct="%1.0f%%",
            pctdistance=0.75,
            startangle=140,
            wedgeprops=dict(width=0.45, edgecolor=self.CARD_DARK, linewidth=2)
        )

        for text in texts:
            text.set_color(self.TEXT_LIGHT)
            text.set_fontsize(8)

        for autotext in autotexts:
            autotext.set_color(self.TEXT_LIGHT)
            autotext.set_fontsize(8)
            autotext.set_fontweight("bold")

        ax.set_title("Subject Distribution", color=self.TEXT_LIGHT, fontsize=11, fontweight="bold", pad=10)
        fig.tight_layout()
        return fig
