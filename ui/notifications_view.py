"""
==============================================================================
StudySphere — Notifications & Reminders View
==============================================================================
Author: Senior Python Mentor & Architect
Role: Dedicated notification center surfacing overdue alerts, upcoming
      assignment deadlines, and daily focus targets with inline actions.
"""

import customtkinter as ctk
from ui.theme import Theme
from modules.notifications import NotificationManager
from modules.task_manager import TaskManager


class NotificationsView(ctk.CTkScrollableFrame):
    """
    Academic Notification Center.
    """

    def __init__(self, master, notif_mgr: NotificationManager, task_mgr: TaskManager, on_navigate, **kwargs):
        super().__init__(
            master,
            fg_color=Theme.BG_CONTENT,
            **kwargs
        )
        self.notif_mgr = notif_mgr
        self.task_mgr = task_mgr
        self.on_navigate = on_navigate

        self._build_header()
        self._build_summary_row()
        self._build_notifications_list()
        self.refresh()

    def _build_header(self) -> None:
        """Header banner."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 16))

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left")

        h1 = ctk.CTkLabel(left, text="Academic Notifications & Alerts", font=Theme.font_title(), text_color=Theme.TEXT_PRIMARY)
        h1.pack(anchor="w")

        sub = ctk.CTkLabel(
            left,
            text="Proactive reminders for impending deadlines, overdue submissions, and daily study targets.",
            font=Theme.font_body(),
            text_color=Theme.TEXT_MUTED
        )
        sub.pack(anchor="w")

    def _build_summary_row(self) -> None:
        """3 summary cards for alert levels."""
        self.summary_box = ctk.CTkFrame(self, fg_color="transparent")
        self.summary_box.pack(fill="x", padx=24, pady=(0, 20))
        for i in range(3):
            self.summary_box.grid_columnconfigure(i, weight=1, uniform="notif_sum")

    def _build_notifications_list(self) -> None:
        """Scrollable notifications list."""
        self.list_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, padx=24, pady=(0, 24))

    def refresh(self) -> None:
        """Evaluates alerts and re-renders view."""
        self._render_summary()
        self._render_alerts()

    def _render_summary(self) -> None:
        for w in self.summary_box.winfo_children():
            w.destroy()

        counts = self.notif_mgr.get_notification_counts()

        cards = [
            ("CRITICAL OVERDUE", str(counts["critical"]), "Requires immediate attention", Theme.ACCENT_ROSE),
            ("IMMINENT DEADLINES", str(counts["warning"]), "Due in the next 48 hours", Theme.ACCENT_AMBER),
            ("STUDY TARGETS", str(counts["info"]), "Daily progress & achievements", Theme.ACCENT_PRIMARY)
        ]

        for idx, (title, val, sub, col) in enumerate(cards):
            c = ctk.CTkFrame(self.summary_box, fg_color=Theme.BG_CARD, border_color=Theme.BORDER, border_width=1, corner_radius=10)
            c.grid(row=0, column=idx, padx=6, sticky="nsew")

            inner = ctk.CTkFrame(c, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=14, pady=12)

            ctk.CTkLabel(inner, text=title, font=Theme.font_small_bold(), text_color=Theme.TEXT_MUTED).pack(anchor="w")
            ctk.CTkLabel(inner, text=val, font=Theme.font_stat_number(), text_color=col).pack(anchor="w", pady=(2, 0))
            ctk.CTkLabel(inner, text=sub, font=Theme.font_small(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w")

    def _render_alerts(self) -> None:
        for w in self.list_frame.winfo_children():
            w.destroy()

        alerts = self.notif_mgr.get_all_notifications()

        if not alerts:
            empty = ctk.CTkFrame(self.list_frame, fg_color=Theme.BG_CARD, corner_radius=10)
            empty.pack(fill="x", pady=40)
            ctk.CTkLabel(
                empty,
                text="🎉 All caught up! No overdue assignments or pending deadline warnings.",
                font=Theme.font_body(),
                text_color=Theme.TEXT_MUTED
            ).pack(pady=30)
            return

        for a in alerts:
            card = ctk.CTkFrame(
                self.list_frame,
                fg_color=Theme.BG_CARD,
                border_color=a["color"],
                border_width=1,
                corner_radius=8
            )
            card.pack(fill="x", pady=5)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=16, pady=12)

            # Left side: severity pill & text
            left = ctk.CTkFrame(inner, fg_color="transparent")
            left.pack(side="left", fill="x", expand=True)

            pill_row = ctk.CTkFrame(left, fg_color="transparent")
            pill_row.pack(anchor="w")

            ctk.CTkLabel(
                pill_row,
                text=f" {a['severity']} ",
                font=Theme.font_small_bold(),
                fg_color=a["color"],
                text_color="#FFFFFF",
                corner_radius=4
            ).pack(side="left", padx=(0, 8))

            ctk.CTkLabel(
                pill_row,
                text=a["title"],
                font=Theme.font_body_bold(),
                text_color=Theme.TEXT_PRIMARY
            ).pack(side="left")

            ctk.CTkLabel(
                left,
                text=a["message"],
                font=Theme.font_body(),
                text_color=Theme.TEXT_SECONDARY,
                anchor="w"
            ).pack(anchor="w", pady=(4, 0))

            # Right action button if linked to task
            if a.get("task_id"):
                right = ctk.CTkFrame(inner, fg_color="transparent")
                right.pack(side="right", padx=(12, 0))

                done_btn = ctk.CTkButton(
                    right,
                    text="✓ Mark Done",
                    font=Theme.font_small_bold(),
                    width=90,
                    height=30,
                    corner_radius=6,
                    fg_color=Theme.BG_SIDEBAR,
                    hover_color=Theme.ACCENT_EMERALD,
                    text_color=Theme.TEXT_PRIMARY,
                    command=lambda tid=a["task_id"]: self._mark_task_done(tid)
                )
                done_btn.pack()

    def _mark_task_done(self, task_id: int) -> None:
        self.task_mgr.toggle_task_status(task_id)
        self.refresh()
