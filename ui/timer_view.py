"""
==============================================================================
StudySphere — Focus Timer (Pomodoro) View
==============================================================================
Author: Senior Python Mentor & Architect
Role: Interactive Pomodoro study environment. Non-blocking countdown loop
      using Tkinter's `after()`, custom mode selection, subject association,
      audio-visual completion alerts, and session persistence to SQLite.
"""

import customtkinter as ctk
from tkinter import messagebox
from ui.theme import Theme
from modules.focus_timer import FocusTimer
from modules.subject_manager import SubjectManager


class TimerView(ctk.CTkScrollableFrame):
    """
    Pomodoro Focus Timer interface.
    """

    def __init__(self, master, timer_mgr: FocusTimer, subject_mgr: SubjectManager, **kwargs):
        super().__init__(
            master,
            fg_color=Theme.BG_CONTENT,
            **kwargs
        )
        self.timer_mgr = timer_mgr
        self.subject_mgr = subject_mgr

        self.timer_job = None
        self.subjects = []
        self.subject_map = {}

        # Set callbacks on timer manager
        self.timer_mgr.on_tick_callback = self._on_tick
        self.timer_mgr.on_complete_callback = self._on_complete

        self._build_layout()
        self.refresh()

    def _build_layout(self) -> None:
        """Constructs timer UI components."""
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 14))

        h1 = ctk.CTkLabel(header, text="Focus Timer", font=Theme.font_title(), text_color=Theme.TEXT_PRIMARY)
        h1.pack(anchor="w")

        sub = ctk.CTkLabel(
            header,
            text="Boost deep-work productivity with Pomodoro intervals linked to your courses.",
            font=Theme.font_body(),
            text_color=Theme.TEXT_MUTED
        )
        sub.pack(anchor="w")

        # Center Main Timer Card
        self.card = ctk.CTkFrame(
            self,
            fg_color=Theme.BG_CARD,
            border_color=Theme.BORDER,
            border_width=1,
            corner_radius=12
        )
        self.card.pack(fill="x", padx=24, pady=(0, 20))

        # Mode Selection Segmented Button
        mode_box = ctk.CTkFrame(self.card, fg_color="transparent")
        mode_box.pack(fill="x", padx=24, pady=(20, 16))

        self.mode_var = ctk.StringVar(value="Focus (25m)")
        self.mode_segmented = ctk.CTkSegmentedButton(
            mode_box,
            values=["Focus (25m)", "Short Break (5m)", "Long Break (15m)", "Custom (45m)"],
            variable=self.mode_var,
            font=Theme.font_body_bold(),
            selected_color=Theme.ACCENT_PRIMARY,
            selected_hover_color=Theme.ACCENT_PRIMARY_HOVER,
            command=self._handle_mode_change
        )
        self.mode_segmented.pack(anchor="center")

        # Big Countdown Digits
        self.time_label = ctk.CTkLabel(
            self.card,
            text="25:00",
            font=Theme.font_timer(),
            text_color=Theme.TEXT_PRIMARY
        )
        self.time_label.pack(pady=(10, 14))

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(
            self.card,
            width=450,
            height=10,
            corner_radius=5,
            progress_color=Theme.ACCENT_PRIMARY,
            fg_color=Theme.BG_INPUT
        )
        self.progress_bar.pack(pady=(0, 20))
        self.progress_bar.set(0.0)

        # Subject & Notes controls
        inputs_row = ctk.CTkFrame(self.card, fg_color="transparent")
        inputs_row.pack(fill="x", padx=40, pady=(0, 20))
        inputs_row.grid_columnconfigure((0, 1), weight=1)

        # Subject Selector
        sub_box = ctk.CTkFrame(inputs_row, fg_color="transparent")
        sub_box.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkLabel(sub_box, text="Study Subject:", font=Theme.font_small_bold(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 2))
        self.subject_var = ctk.StringVar(value="General Focus")
        self.subject_dropdown = ctk.CTkOptionMenu(
            sub_box,
            variable=self.subject_var,
            values=["General Focus"],
            font=Theme.font_body(),
            height=34,
            fg_color=Theme.BG_INPUT,
            button_color=Theme.BG_SIDEBAR,
            command=self._on_subject_changed
        )
        self.subject_dropdown.pack(fill="x")

        # Session Note Entry
        notes_box = ctk.CTkFrame(inputs_row, fg_color="transparent")
        notes_box.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        ctk.CTkLabel(notes_box, text="Session Objective:", font=Theme.font_small_bold(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 2))
        self.note_entry = ctk.CTkEntry(
            notes_box,
            placeholder_text="e.g. Implement NumPy matrix multiplication",
            font=Theme.font_body(),
            height=34,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER
        )
        self.note_entry.pack(fill="x")

        # Control Buttons Row: Start/Pause, Reset, Skip
        ctrl_box = ctk.CTkFrame(self.card, fg_color="transparent")
        ctrl_box.pack(pady=(0, 24))

        self.start_btn = ctk.CTkButton(
            ctrl_box,
            text="▶ Start Focus",
            font=Theme.font_body_bold(),
            width=140,
            height=40,
            corner_radius=8,
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color=Theme.ACCENT_PRIMARY_HOVER,
            command=self._toggle_start_pause
        )
        self.start_btn.pack(side="left", padx=6)

        self.reset_btn = ctk.CTkButton(
            ctrl_box,
            text="↺ Reset",
            font=Theme.font_body(),
            width=90,
            height=40,
            corner_radius=8,
            fg_color=Theme.BG_SIDEBAR,
            hover_color=Theme.BG_CARD_HOVER,
            border_color=Theme.BORDER,
            border_width=1,
            command=self._reset_timer
        )
        self.reset_btn.pack(side="left", padx=6)

        self.skip_btn = ctk.CTkButton(
            ctrl_box,
            text="⏭ Skip",
            font=Theme.font_body(),
            width=90,
            height=40,
            corner_radius=8,
            fg_color=Theme.BG_SIDEBAR,
            hover_color=Theme.BG_CARD_HOVER,
            border_color=Theme.BORDER,
            border_width=1,
            command=self._skip_session
        )
        self.skip_btn.pack(side="left", padx=6)

        # ----------------------------------------------------------------------
        # Lower Statistics & Session Feed
        # ----------------------------------------------------------------------
        self.stats_row = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_row.pack(fill="x", padx=24, pady=(0, 20))
        for i in range(3):
            self.stats_row.grid_columnconfigure(i, weight=1, uniform="timer_stat")

        # History Card
        self.history_card = ctk.CTkFrame(
            self,
            fg_color=Theme.BG_CARD,
            border_color=Theme.BORDER,
            border_width=1,
            corner_radius=10
        )
        self.history_card.pack(fill="x", padx=24, pady=(0, 24))

    def refresh(self) -> None:
        """Refreshes subject options and study metrics."""
        self.subjects = self.subject_mgr.get_all_subjects()
        self.subject_map = {s["name"]: s["id"] for s in self.subjects}

        vals = ["General Focus"] + list(self.subject_map.keys())
        self.subject_dropdown.configure(values=vals)

        # Refresh stats cards
        for widget in self.stats_row.winfo_children():
            widget.destroy()

        today_mins = self.timer_mgr.get_today_study_minutes()
        all_hours = self.timer_mgr.get_total_study_hours()
        recent = self.timer_mgr.get_recent_sessions(limit=5)
        completed_today_count = sum(1 for s in recent if s.get("completed_at", "").startswith(today_mins > 0 and s["completed_at"][:10] or "9999"))

        stats_data = [
            ("TODAY'S FOCUS TIME", f"{today_mins:.0f} mins", "Target: 120 mins", Theme.ACCENT_PRIMARY),
            ("ALL-TIME STUDY HOURS", f"{all_hours:.1f} hrs", "Across all subjects", Theme.ACCENT_EMERALD),
            ("COMPLETED SESSIONS", f"{len(recent)} logged", "In recent history", Theme.ACCENT_BLUE),
        ]

        for idx, (title, val, sub, col) in enumerate(stats_data):
            c = ctk.CTkFrame(self.stats_row, fg_color=Theme.BG_CARD, border_color=Theme.BORDER, border_width=1, corner_radius=10)
            c.grid(row=0, column=idx, padx=6, sticky="nsew")

            inner = ctk.CTkFrame(c, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=14, pady=12)

            ctk.CTkLabel(inner, text=title, font=Theme.font_small_bold(), text_color=Theme.TEXT_MUTED).pack(anchor="w")
            ctk.CTkLabel(inner, text=val, font=Theme.font_stat_number(), text_color=col).pack(anchor="w", pady=(2, 0))
            ctk.CTkLabel(inner, text=sub, font=Theme.font_small(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w")

        # Refresh history feed
        for widget in self.history_card.winfo_children():
            widget.destroy()

        h_title = ctk.CTkLabel(self.history_card, text="📜 Study Session Log", font=Theme.font_h2(), text_color=Theme.TEXT_PRIMARY)
        h_title.pack(anchor="w", padx=16, pady=(12, 8))

        if not recent:
            ctk.CTkLabel(
                self.history_card,
                text="No focus intervals recorded yet. Hit 'Start Focus' to log your first interval!",
                font=Theme.font_body(),
                text_color=Theme.TEXT_MUTED
            ).pack(padx=16, pady=20)
            return

        for s in recent:
            row = ctk.CTkFrame(self.history_card, fg_color=Theme.BG_SIDEBAR, corner_radius=6)
            row.pack(fill="x", padx=16, pady=4)

            r_inner = ctk.CTkFrame(row, fg_color="transparent")
            r_inner.pack(fill="x", padx=12, pady=6)

            tag_col = s.get("subject_color") or Theme.ACCENT_PRIMARY
            sub_name = s.get("subject_name") or "General"

            lbl = ctk.CTkLabel(
                r_inner,
                text=f"🎯 {s['session_type']} ({s['duration_minutes']:.0f}m) • {sub_name}",
                font=Theme.font_body_bold(),
                text_color=Theme.TEXT_PRIMARY
            )
            lbl.pack(side="left")

            if s.get("notes"):
                note_lbl = ctk.CTkLabel(
                    r_inner,
                    text=f"— {s['notes']}",
                    font=Theme.font_small(),
                    text_color=Theme.TEXT_MUTED
                )
                note_lbl.pack(side="left", padx=(8, 0))

            ts = ctk.CTkLabel(
                r_inner,
                text=s.get("completed_at", "")[:16],
                font=Theme.font_small(),
                text_color=Theme.TEXT_SECONDARY
            )
            ts.pack(side="right")

    # --------------------------------------------------------------------------
    # Timer Event Logic
    # --------------------------------------------------------------------------
    def _handle_mode_change(self, mode_str: str) -> None:
        """Switches Pomodoro session type."""
        self._stop_tick_loop()
        self.start_btn.configure(text="▶ Start Focus", fg_color=Theme.ACCENT_PRIMARY)

        if "Short Break" in mode_str:
            self.timer_mgr.set_session_type(FocusTimer.TYPE_SHORT_BREAK)
        elif "Long Break" in mode_str:
            self.timer_mgr.set_session_type(FocusTimer.TYPE_LONG_BREAK)
        elif "Custom" in mode_str:
            self.timer_mgr.set_session_type(FocusTimer.TYPE_FOCUS, custom_minutes=45)
        else:
            self.timer_mgr.set_session_type(FocusTimer.TYPE_FOCUS)

        self.time_label.configure(text=self.timer_mgr.get_formatted_time())
        self.progress_bar.set(0.0)

    def _on_subject_changed(self, choice: str) -> None:
        """Sets active subject ID on timer manager."""
        self.timer_mgr.active_subject_id = self.subject_map.get(choice)

    def _toggle_start_pause(self) -> None:
        """Starts or pauses the non-blocking timer."""
        # Grab note
        self.timer_mgr.session_notes = self.note_entry.get().strip()

        if self.timer_mgr.state == FocusTimer.STATE_RUNNING:
            self.timer_mgr.pause()
            self._stop_tick_loop()
            self.start_btn.configure(text="▶ Resume", fg_color=Theme.ACCENT_PRIMARY)
        else:
            self.timer_mgr.start()
            self.start_btn.configure(text="⏸ Pause", fg_color=Theme.ACCENT_AMBER)
            self._schedule_tick()

    def _reset_timer(self) -> None:
        """Resets timer back to initial duration."""
        self._stop_tick_loop()
        self.timer_mgr.reset()
        self.start_btn.configure(text="▶ Start Focus", fg_color=Theme.ACCENT_PRIMARY)
        self.time_label.configure(text=self.timer_mgr.get_formatted_time())
        self.progress_bar.set(0.0)

    def _skip_session(self) -> None:
        """Skips remainder of session."""
        self._stop_tick_loop()
        self._reset_timer()

    def _schedule_tick(self) -> None:
        """Schedules non-blocking tick after 1000 milliseconds."""
        self.timer_job = self.after(1000, self._timer_tick)

    def _stop_tick_loop(self) -> None:
        if self.timer_job:
            self.after_cancel(self.timer_job)
            self.timer_job = None

    def _timer_tick(self) -> None:
        """Invoked every 1000ms."""
        finished = self.timer_mgr.tick()
        if not finished and self.timer_mgr.state == FocusTimer.STATE_RUNNING:
            self._schedule_tick()

    def _on_tick(self, remaining_sec: int, progress: float) -> None:
        """Updates digit display and progress bar."""
        self.time_label.configure(text=self.timer_mgr.get_formatted_time())
        self.progress_bar.set(progress)

    def _on_complete(self, session_type: str) -> None:
        """Fires when timer countdown reaches 00:00."""
        self._stop_tick_loop()
        self.start_btn.configure(text="▶ Start Focus", fg_color=Theme.ACCENT_PRIMARY)
        self.progress_bar.set(1.0)
        self.time_label.configure(text="00:00")

        # Sound chime alert via Tkinter bell
        try:
            self.bell()
        except Exception:
            pass

        self.refresh()
        messagebox.showinfo(
            "Session Completed! 🎉",
            f"Great job! Your {session_type} interval has completed and has been logged to your database."
        )
        self._reset_timer()
