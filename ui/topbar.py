"""
==============================================================================
StudySphere — Topbar Header Component
==============================================================================
Author: Senior Python Mentor & Architect
Role: Renders the top navigation header with current date, rotating student
      motivational quotes, quick-action shortcuts, and notification trigger.
"""

from datetime import datetime
import customtkinter as ctk
from ui.theme import Theme


class Topbar(ctk.CTkFrame):
    """
    Header bar sitting atop the content pane.
    """

    MOTIVATIONAL_QUOTES = [
        "\"First, solve the problem. Then, write the code.\" — John Johnson",
        "\"Simplicity is prerequisite for reliability.\" — Edsger W. Dijkstra",
        "\"The only way to learn a new programming language is by writing programs in it.\" — Dennis Ritchie",
        "\"Talk is cheap. Show me the code.\" — Linus Torvalds",
        "\"Data is the new oil, but analytics is the refinery.\" — Data Science Proverb",
        "\"Small daily improvements over time lead to stunning results.\" — Robin Sharma",
        "\"Consistency separates the amateurs from the professionals.\" — Anonymous"
    ]

    def __init__(self, master, on_quick_task, on_quick_timer, on_view_notifications, **kwargs):
        super().__init__(
            master,
            height=60,
            corner_radius=0,
            fg_color=Theme.BG_SIDEBAR,
            border_color=Theme.BORDER,
            border_width=1,
            **kwargs
        )
        self.pack_propagate(False)

        self.on_quick_task = on_quick_task
        self.on_quick_timer = on_quick_timer
        self.on_view_notifications = on_view_notifications

        self._build_ui()

    def _build_ui(self) -> None:
        """Constructs topbar content."""
        # Left Section: Date & Rotating Quote
        left_box = ctk.CTkFrame(self, fg_color="transparent")
        left_box.pack(side="left", padx=20, fill="y")

        now = datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        
        # Pick quote based on day-of-year for stability throughout the day
        quote_idx = now.timetuple().tm_yday % len(self.MOTIVATIONAL_QUOTES)
        current_quote = self.MOTIVATIONAL_QUOTES[quote_idx]

        date_label = ctk.CTkLabel(
            left_box,
            text=f"📅 {date_str}",
            font=Theme.font_body_bold(),
            text_color=Theme.TEXT_PRIMARY
        )
        date_label.pack(anchor="w", pady=(8, 0))

        quote_label = ctk.CTkLabel(
            left_box,
            text=current_quote,
            font=Theme.font_small(),
            text_color=Theme.TEXT_MUTED
        )
        quote_label.pack(anchor="w")

        # Right Section: Quick Action Buttons & Notification Bell
        right_box = ctk.CTkFrame(self, fg_color="transparent")
        right_box.pack(side="right", padx=20, fill="y")

        # Quick Task Button
        add_task_btn = ctk.CTkButton(
            right_box,
            text="+ Add Task",
            font=Theme.font_small_bold(),
            height=32,
            width=100,
            corner_radius=6,
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color=Theme.ACCENT_PRIMARY_HOVER,
            command=self.on_quick_task
        )
        add_task_btn.pack(side="left", padx=(0, 8), pady=14)

        # Quick Timer Button
        timer_btn = ctk.CTkButton(
            right_box,
            text="⏱️ Focus",
            font=Theme.font_small_bold(),
            height=32,
            width=80,
            corner_radius=6,
            fg_color=Theme.BG_CARD,
            hover_color=Theme.BG_CARD_HOVER,
            border_color=Theme.BORDER,
            border_width=1,
            text_color=Theme.TEXT_PRIMARY,
            command=self.on_quick_timer
        )
        timer_btn.pack(side="left", padx=(0, 8), pady=14)

        # Notification Bell
        self.bell_btn = ctk.CTkButton(
            right_box,
            text="🔔",
            font=("Segoe UI Emoji", 14),
            height=32,
            width=40,
            corner_radius=6,
            fg_color=Theme.BG_CARD,
            hover_color=Theme.BG_CARD_HOVER,
            border_color=Theme.BORDER,
            border_width=1,
            text_color=Theme.TEXT_PRIMARY,
            command=self.on_view_notifications
        )
        self.bell_btn.pack(side="left", pady=14)

    def set_badge_indicator(self, has_alerts: bool) -> None:
        """Visual cue on bell when unread notifications are present."""
        if has_alerts:
            self.bell_btn.configure(
                text="🔔🔴",
                border_color=Theme.ACCENT_ROSE
            )
        else:
            self.bell_btn.configure(
                text="🔔",
                border_color=Theme.BORDER
            )
