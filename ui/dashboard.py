"""
==============================================================================
StudySphere — Dashboard View
==============================================================================
Author: Senior Python Mentor & Architect
Role: The central command center screen. Computes and renders real database
      metrics: task progress, focus hours, embedded mini-chart, upcoming
      deadlines, and recent study activity.
"""

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ui.theme import Theme
from modules.task_manager import TaskManager
from modules.subject_manager import SubjectManager
from modules.focus_timer import FocusTimer
from modules.analytics import AnalyticsEngine


class DashboardView(ctk.CTkScrollableFrame):
    """
    SaaS-style productivity dashboard screen.
    """

    def __init__(self, master, task_mgr: TaskManager, subject_mgr: SubjectManager,
                 timer_mgr: FocusTimer, analytics_mgr: AnalyticsEngine, on_navigate, **kwargs):
        super().__init__(
            master,
            fg_color=Theme.BG_CONTENT,
            **kwargs
        )
        self.task_mgr = task_mgr
        self.subject_mgr = subject_mgr
        self.timer_mgr = timer_mgr
        self.analytics_mgr = analytics_mgr
        self.on_navigate = on_navigate

        self.canvas_widget = None

        self._build_layout()
        self.refresh()

    def _build_layout(self) -> None:
        """Constructs layout skeleton."""
        # Page Title Banner
        title_box = ctk.CTkFrame(self, fg_color="transparent")
        title_box.pack(fill="x", padx=24, pady=(20, 16))

        h1 = ctk.CTkLabel(
            title_box,
            text="Academic Command Center",
            font=Theme.font_title(),
            text_color=Theme.TEXT_PRIMARY
        )
        h1.pack(anchor="w")

        sub = ctk.CTkLabel(
            title_box,
            text="Track your deadlines, focus momentum, and course progress in real time.",
            font=Theme.font_body(),
            text_color=Theme.TEXT_MUTED
        )
        sub.pack(anchor="w", pady=(2, 0))

        # 1. Top Metrics Cards Row
        self.cards_row = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_row.pack(fill="x", padx=24, pady=(0, 20))
        for col_idx in range(4):
            self.cards_row.grid_columnconfigure(col_idx, weight=1, uniform="metric_cards")

        # 2. Main Dual-Column Content Grid
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        self.grid_frame.grid_columnconfigure(0, weight=3) # Left column (Chart + Quick links)
        self.grid_frame.grid_columnconfigure(1, weight=2) # Right column (Deadlines + Feed)

        # Left Column Container
        self.left_col = ctk.CTkFrame(self.grid_frame, fg_color="transparent")
        self.left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        # Right Column Container
        self.right_col = ctk.CTkFrame(self.grid_frame, fg_color="transparent")
        self.right_col.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

    def refresh(self) -> None:
        """
        Recalculates all values from database and refreshes view.
        """
        self._render_metric_cards()
        self._render_productivity_chart()
        self._render_deadlines_widget()
        self._render_recent_sessions_widget()

    def _render_metric_cards(self) -> None:
        """Renders 4 modern metric cards."""
        for widget in self.cards_row.winfo_children():
            widget.destroy()

        task_counts = self.task_mgr.get_task_counts()
        today_mins = self.timer_mgr.get_today_study_minutes()
        today_hrs = round(today_mins / 60.0, 1)
        subjects = self.subject_mgr.get_all_subjects()

        card_configs = [
            {
                "title": "TOTAL TASKS",
                "value": str(task_counts["total"]),
                "sub": f"{task_counts['completed']} Completed ({task_counts['completion_rate']}%)",
                "color": Theme.ACCENT_PRIMARY,
                "icon": "📋"
            },
            {
                "title": "STUDY TODAY",
                "value": f"{today_hrs}h",
                "sub": f"{today_mins:.0f} / 120 min daily goal",
                "color": Theme.ACCENT_EMERALD,
                "icon": "⏱️"
            },
            {
                "title": "ACTIVE SUBJECTS",
                "value": str(len(subjects)),
                "sub": "Enrolled courses",
                "color": Theme.ACCENT_BLUE,
                "icon": "📚"
            },
            {
                "title": "OVERDUE TASKS",
                "value": str(task_counts["overdue"]),
                "sub": "Immediate action required" if task_counts["overdue"] > 0 else "All caught up!",
                "color": Theme.ACCENT_ROSE if task_counts["overdue"] > 0 else Theme.ACCENT_EMERALD,
                "icon": "⚠️" if task_counts["overdue"] > 0 else "✨"
            }
        ]

        for idx, cfg in enumerate(card_configs):
            card = ctk.CTkFrame(
                self.cards_row,
                fg_color=Theme.BG_CARD,
                border_color=Theme.BORDER,
                border_width=1,
                corner_radius=10
            )
            card.grid(row=0, column=idx, padx=6, sticky="nsew")

            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="both", expand=True, padx=14, pady=12)

            # Top label + icon
            top_line = ctk.CTkFrame(content, fg_color="transparent")
            top_line.pack(fill="x")

            lbl = ctk.CTkLabel(
                top_line,
                text=cfg["title"],
                font=Theme.font_small_bold(),
                text_color=Theme.TEXT_MUTED
            )
            lbl.pack(side="left")

            icon_lbl = ctk.CTkLabel(
                top_line,
                text=cfg["icon"],
                font=("Segoe UI Emoji", 14)
            )
            icon_lbl.pack(side="right")

            # Big Value
            val_lbl = ctk.CTkLabel(
                content,
                text=cfg["value"],
                font=Theme.font_stat_number(),
                text_color=cfg["color"]
            )
            val_lbl.pack(anchor="w", pady=(4, 2))

            # Subtitle
            sub_lbl = ctk.CTkLabel(
                content,
                text=cfg["sub"],
                font=Theme.font_small(),
                text_color=Theme.TEXT_SECONDARY
            )
            sub_lbl.pack(anchor="w")

    def _render_productivity_chart(self) -> None:
        """Renders the Matplotlib chart embedded in the left column."""
        for widget in self.left_col.winfo_children():
            widget.destroy()

        chart_card = ctk.CTkFrame(
            self.left_col,
            fg_color=Theme.BG_CARD,
            border_color=Theme.BORDER,
            border_width=1,
            corner_radius=10
        )
        chart_card.pack(fill="x", pady=(0, 16))

        # Chart Header
        header = ctk.CTkFrame(chart_card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 6))

        title = ctk.CTkLabel(
            header,
            text="📊 Weekly Study Momentum",
            font=Theme.font_h2(),
            text_color=Theme.TEXT_PRIMARY
        )
        title.pack(side="left")

        # Generate Matplotlib Figure
        fig = self.analytics_mgr.create_daily_hours_chart(days=7)
        canvas = FigureCanvasTkAgg(fig, master=chart_card)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # Quick Actions Card under Chart
        actions_card = ctk.CTkFrame(
            self.left_col,
            fg_color=Theme.BG_CARD,
            border_color=Theme.BORDER,
            border_width=1,
            corner_radius=10
        )
        actions_card.pack(fill="x")

        act_head = ctk.CTkLabel(
            actions_card,
            text="🚀 Quick Shortcuts",
            font=Theme.font_h2(),
            text_color=Theme.TEXT_PRIMARY
        )
        act_head.pack(anchor="w", padx=16, pady=(12, 8))

        btn_row = ctk.CTkFrame(actions_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(0, 14))
        btn_row.grid_columnconfigure((0, 1, 2), weight=1)

        b1 = ctk.CTkButton(
            btn_row,
            text="⏱️ Start Pomodoro",
            font=Theme.font_small_bold(),
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color=Theme.ACCENT_PRIMARY_HOVER,
            command=lambda: self.on_navigate("timer")
        )
        b1.grid(row=0, column=0, padx=4, sticky="ew")

        b2 = ctk.CTkButton(
            btn_row,
            text="💡 Test Knowledge",
            font=Theme.font_small_bold(),
            fg_color=Theme.BG_SIDEBAR,
            hover_color=Theme.BG_CARD_HOVER,
            border_color=Theme.BORDER,
            border_width=1,
            command=lambda: self.on_navigate("quiz")
        )
        b2.grid(row=0, column=1, padx=4, sticky="ew")

        b3 = ctk.CTkButton(
            btn_row,
            text="📝 New Note",
            font=Theme.font_small_bold(),
            fg_color=Theme.BG_SIDEBAR,
            hover_color=Theme.BG_CARD_HOVER,
            border_color=Theme.BORDER,
            border_width=1,
            command=lambda: self.on_navigate("notes")
        )
        b3.grid(row=0, column=2, padx=4, sticky="ew")

    def _render_deadlines_widget(self) -> None:
        """Renders upcoming deadlines in the right column."""
        for widget in self.right_col.winfo_children():
            widget.destroy()

        deadlines_card = ctk.CTkFrame(
            self.right_col,
            fg_color=Theme.BG_CARD,
            border_color=Theme.BORDER,
            border_width=1,
            corner_radius=10
        )
        deadlines_card.pack(fill="x", pady=(0, 16))

        header = ctk.CTkFrame(deadlines_card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 8))

        title = ctk.CTkLabel(
            header,
            text="⏳ Upcoming Deadlines",
            font=Theme.font_h2(),
            text_color=Theme.TEXT_PRIMARY
        )
        title.pack(side="left")

        view_all = ctk.CTkButton(
            header,
            text="View All →",
            font=Theme.font_small_bold(),
            width=70,
            height=24,
            fg_color="transparent",
            text_color=Theme.ACCENT_LIGHT,
            hover_color=Theme.BG_CARD_HOVER,
            command=lambda: self.on_navigate("tasks")
        )
        view_all.pack(side="right")

        upcoming = self.task_mgr.get_upcoming_deadlines(limit=4)
        overdue = self.task_mgr.get_overdue_tasks()[:2] # Top 2 overdue if any

        # Show overdue first
        combined = overdue + upcoming

        if not combined:
            empty = ctk.CTkLabel(
                deadlines_card,
                text="🎉 No pending deadlines! You're completely caught up.",
                font=Theme.font_body(),
                text_color=Theme.TEXT_MUTED,
                justify="center"
            )
            empty.pack(padx=16, pady=24)
            return

        for t in combined[:5]:
            item = ctk.CTkFrame(deadlines_card, fg_color=Theme.BG_SIDEBAR, corner_radius=8)
            item.pack(fill="x", padx=14, pady=4)

            inner = ctk.CTkFrame(item, fg_color="transparent")
            inner.pack(fill="x", padx=10, pady=8)

            # Left column: title & course
            left = ctk.CTkFrame(inner, fg_color="transparent")
            left.pack(side="left", fill="x", expand=True)

            t_title = ctk.CTkLabel(
                left,
                text=t["title"],
                font=Theme.font_body_bold(),
                text_color=Theme.TEXT_PRIMARY,
                anchor="w"
            )
            t_title.pack(anchor="w")

            course_text = t["subject_code"] or "General"
            sub_lbl = ctk.CTkLabel(
                left,
                text=f"{course_text} • Priority: {t['priority']}",
                font=Theme.font_small(),
                text_color=t["subject_color"] or Theme.TEXT_MUTED,
                anchor="w"
            )
            sub_lbl.pack(anchor="w")

            # Right badge: Days remaining or Overdue
            right = ctk.CTkFrame(inner, fg_color="transparent")
            right.pack(side="right")

            if t.get("is_overdue") or t.get("days_overdue"):
                badge_text = "OVERDUE"
                badge_color = Theme.ACCENT_ROSE
            elif t.get("days_remaining", 0) == 0:
                badge_text = "DUE TODAY"
                badge_color = Theme.ACCENT_AMBER
            else:
                days = t.get("days_remaining", 1)
                badge_text = f"In {days}d"
                badge_color = Theme.ACCENT_BLUE

            badge = ctk.CTkLabel(
                right,
                text=f" {badge_text} ",
                font=Theme.font_small_bold(),
                fg_color=badge_color,
                text_color="#FFFFFF",
                corner_radius=4
            )
            badge.pack()

    def _render_recent_sessions_widget(self) -> None:
        """Renders recent focus session feed."""
        feed_card = ctk.CTkFrame(
            self.right_col,
            fg_color=Theme.BG_CARD,
            border_color=Theme.BORDER,
            border_width=1,
            corner_radius=10
        )
        feed_card.pack(fill="x")

        header = ctk.CTkFrame(feed_card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 8))

        title = ctk.CTkLabel(
            header,
            text="🕒 Recent Study Activity",
            font=Theme.font_h2(),
            text_color=Theme.TEXT_PRIMARY
        )
        title.pack(side="left")

        sessions = self.timer_mgr.get_recent_sessions(limit=4)
        if not sessions:
            empty = ctk.CTkLabel(
                feed_card,
                text="No recent study sessions logged.\nStart your first focus session today!",
                font=Theme.font_body(),
                text_color=Theme.TEXT_MUTED
            )
            empty.pack(padx=16, pady=20)
            return

        for s in sessions:
            row = ctk.CTkFrame(feed_card, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=4)

            time_str = s["completed_at"][:16] if s.get("completed_at") else ""
            sub_name = s.get("subject_name") or "General Study"

            lbl = ctk.CTkLabel(
                row,
                text=f"🎯 {s['session_type']} ({s['duration_minutes']:.0f}m) — {sub_name}",
                font=Theme.font_body(),
                text_color=Theme.TEXT_PRIMARY
            )
            lbl.pack(side="left")

            ts = ctk.CTkLabel(
                row,
                text=time_str,
                font=Theme.font_small(),
                text_color=Theme.TEXT_MUTED
            )
            ts.pack(side="right")
