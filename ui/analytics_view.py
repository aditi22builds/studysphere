"""
==============================================================================
StudySphere — Analytics & Data Science View
==============================================================================
Author: Senior Python Mentor & Architect
Role: Showcases portfolio-grade data science integration with NumPy statistical
      aggregations and embedded dark-themed Matplotlib visual charts.
"""

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ui.theme import Theme
from modules.analytics import AnalyticsEngine
from modules.focus_timer import FocusTimer


class AnalyticsView(ctk.CTkScrollableFrame):
    """
    Data-driven academic productivity analytics workspace.
    """

    def __init__(self, master, analytics_mgr: AnalyticsEngine, timer_mgr: FocusTimer, **kwargs):
        super().__init__(
            master,
            fg_color=Theme.BG_CONTENT,
            **kwargs
        )
        self.analytics_mgr = analytics_mgr
        self.timer_mgr = timer_mgr

        self.canvas_left = None
        self.canvas_right = None

        self._build_header()
        self._build_stat_cards()
        self._build_chart_grid()
        self._build_session_history()
        self.refresh()

    def _build_header(self) -> None:
        """Renders header banner and refresh action."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 16))

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left")

        h1 = ctk.CTkLabel(left, text="Productivity Analytics", font=Theme.font_title(), text_color=Theme.TEXT_PRIMARY)
        h1.pack(anchor="w")

        sub = ctk.CTkLabel(
            left,
            text="Statistical modeling and distribution analysis powered by NumPy & Matplotlib.",
            font=Theme.font_body(),
            text_color=Theme.TEXT_MUTED
        )
        sub.pack(anchor="w")

        refresh_btn = ctk.CTkButton(
            header,
            text="🔄 Refresh Charts",
            font=Theme.font_body_bold(),
            height=36,
            fg_color=Theme.BG_CARD,
            hover_color=Theme.BG_CARD_HOVER,
            border_color=Theme.BORDER,
            border_width=1,
            command=self.refresh
        )
        refresh_btn.pack(side="right")

    def _build_stat_cards(self) -> None:
        """Container for 4 NumPy-powered summary metrics."""
        self.stats_container = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_container.pack(fill="x", padx=24, pady=(0, 20))
        for i in range(4):
            self.stats_container.grid_columnconfigure(i, weight=1, uniform="ana_cards")

    def _build_chart_grid(self) -> None:
        """Dual-column grid for embedded Matplotlib figures."""
        self.charts_row = ctk.CTkFrame(self, fg_color="transparent")
        self.charts_row.pack(fill="x", padx=24, pady=(0, 20))
        self.charts_row.grid_columnconfigure((0, 1), weight=1)

        # Left chart card (Daily Hours)
        self.left_chart_card = ctk.CTkFrame(
            self.charts_row,
            fg_color=Theme.BG_CARD,
            border_color=Theme.BORDER,
            border_width=1,
            corner_radius=10
        )
        self.left_chart_card.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        # Right chart card (Subject Donut)
        self.right_chart_card = ctk.CTkFrame(
            self.charts_row,
            fg_color=Theme.BG_CARD,
            border_color=Theme.BORDER,
            border_width=1,
            corner_radius=10
        )
        self.right_chart_card.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

    def _build_session_history(self) -> None:
        """Historical session logs container."""
        self.history_frame = ctk.CTkFrame(
            self,
            fg_color=Theme.BG_CARD,
            border_color=Theme.BORDER,
            border_width=1,
            corner_radius=10
        )
        self.history_frame.pack(fill="x", padx=24, pady=(0, 24))

    def refresh(self) -> None:
        """Recalculates NumPy statistics and redraws Matplotlib figures."""
        self._render_stat_cards()
        self._render_charts()
        self._render_history_table()

    def _render_stat_cards(self) -> None:
        for widget in self.stats_container.winfo_children():
            widget.destroy()

        stats = self.analytics_mgr.get_summary_statistics()

        cards_data = [
            ("TOTAL FOCUS TIME", f"{stats['total_hours']}h", f"Across all sessions", Theme.ACCENT_PRIMARY),
            ("MEAN SESSION DURATION", f"{stats['mean_session_min']:.0f}m", f"Median: {stats['median_session_min']:.0f}m (σ = {stats['std_session_min']:.1f}m)", Theme.ACCENT_CYAN),
            ("CONSISTENCY SCORE", f"{stats['consistency_score']:.0f}%", f"{stats['active_days']} of 7 days active", Theme.ACCENT_EMERALD),
            ("STUDY MOMENTUM", stats["trend_direction"], "Linear regression trend", Theme.ACCENT_LIGHT if "Rising" in stats["trend_direction"] else Theme.ACCENT_AMBER)
        ]

        for idx, (title, val, sub, col) in enumerate(cards_data):
            c = ctk.CTkFrame(self.stats_container, fg_color=Theme.BG_CARD, border_color=Theme.BORDER, border_width=1, corner_radius=10)
            c.grid(row=0, column=idx, padx=6, sticky="nsew")

            inner = ctk.CTkFrame(c, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=14, pady=12)

            ctk.CTkLabel(inner, text=title, font=Theme.font_small_bold(), text_color=Theme.TEXT_MUTED).pack(anchor="w")
            ctk.CTkLabel(inner, text=val, font=Theme.font_stat_number(), text_color=col).pack(anchor="w", pady=(2, 0))
            ctk.CTkLabel(inner, text=sub, font=Theme.font_small(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w")

    def _render_charts(self) -> None:
        # Clear previous canvas widgets
        for widget in self.left_chart_card.winfo_children():
            widget.destroy()
        for widget in self.right_chart_card.winfo_children():
            widget.destroy()

        # Build Bar Chart
        fig_bar = self.analytics_mgr.create_daily_hours_chart(days=7)
        self.canvas_left = FigureCanvasTkAgg(fig_bar, master=self.left_chart_card)
        self.canvas_left.draw()
        self.canvas_left.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Build Donut Chart
        fig_donut = self.analytics_mgr.create_subject_donut_chart()
        self.canvas_right = FigureCanvasTkAgg(fig_donut, master=self.right_chart_card)
        self.canvas_right.draw()
        self.canvas_right.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def _render_history_table(self) -> None:
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        title = ctk.CTkLabel(self.history_frame, text="📜 Study Session Log & Subject Breakdown", font=Theme.font_h2(), text_color=Theme.TEXT_PRIMARY)
        title.pack(anchor="w", padx=18, pady=(14, 8))

        sessions = self.timer_mgr.get_recent_sessions(limit=8)
        if not sessions:
            ctk.CTkLabel(
                self.history_frame,
                text="No focus sessions recorded yet.\nStart studying with the timer to see your session logs here!",
                font=Theme.font_body(),
                text_color=Theme.TEXT_MUTED
            ).pack(padx=18, pady=24)
            return

        # Table header
        th = ctk.CTkFrame(self.history_frame, fg_color=Theme.BG_SIDEBAR, corner_radius=6)
        th.pack(fill="x", padx=16, pady=(0, 6))

        ctk.CTkLabel(th, text="Course / Subject", font=Theme.font_small_bold(), text_color=Theme.TEXT_MUTED, width=180, anchor="w").pack(side="left", padx=12, pady=6)
        ctk.CTkLabel(th, text="Interval Type", font=Theme.font_small_bold(), text_color=Theme.TEXT_MUTED, width=120, anchor="w").pack(side="left", padx=6, pady=6)
        ctk.CTkLabel(th, text="Duration", font=Theme.font_small_bold(), text_color=Theme.TEXT_MUTED, width=80, anchor="w").pack(side="left", padx=6, pady=6)
        ctk.CTkLabel(th, text="Session Notes", font=Theme.font_small_bold(), text_color=Theme.TEXT_MUTED, anchor="w").pack(side="left", fill="x", expand=True, padx=6, pady=6)
        ctk.CTkLabel(th, text="Date & Time", font=Theme.font_small_bold(), text_color=Theme.TEXT_MUTED, width=130, anchor="e").pack(side="right", padx=12, pady=6)

        # Rows
        for s in sessions:
            row = ctk.CTkFrame(self.history_frame, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=2)

            sub_name = s.get("subject_name") or "General Study"
            ctk.CTkLabel(row, text=sub_name, font=Theme.font_body_bold(), text_color=s.get("subject_color") or Theme.TEXT_PRIMARY, width=180, anchor="w").pack(side="left", padx=12, pady=4)
            ctk.CTkLabel(row, text=s["session_type"], font=Theme.font_body(), text_color=Theme.TEXT_SECONDARY, width=120, anchor="w").pack(side="left", padx=6, pady=4)
            ctk.CTkLabel(row, text=f"{s['duration_minutes']:.0f}m", font=Theme.font_body_bold(), text_color=Theme.TEXT_PRIMARY, width=80, anchor="w").pack(side="left", padx=6, pady=4)
            ctk.CTkLabel(row, text=s.get("notes") or "—", font=Theme.font_body(), text_color=Theme.TEXT_MUTED, anchor="w").pack(side="left", fill="x", expand=True, padx=6, pady=4)
            ctk.CTkLabel(row, text=s.get("completed_at", "")[:16], font=Theme.font_small(), text_color=Theme.TEXT_MUTED, width=130, anchor="e").pack(side="right", padx=12, pady=4)
