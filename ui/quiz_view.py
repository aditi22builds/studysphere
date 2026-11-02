"""
==============================================================================
StudySphere — Python Knowledge Quiz View
==============================================================================
Author: Senior Python Mentor & Architect
Role: Interactive test arena for evaluating Python & Data Science knowledge.
      Supports randomized question pools, difficulty filtering, live round
      timing, comprehensive score breakdowns with explanations, and attempt archiving.
"""

from datetime import datetime
import customtkinter as ctk
from ui.theme import Theme
from modules.quiz import QuizManager


class QuizView(ctk.CTkScrollableFrame):
    """
    Python technical assessment arena.
    """

    SCREEN_START = "START"
    SCREEN_QUIZ = "QUIZ"
    SCREEN_RESULTS = "RESULTS"
    SCREEN_HISTORY = "HISTORY"

    def __init__(self, master, quiz_mgr: QuizManager, **kwargs):
        super().__init__(
            master,
            fg_color=Theme.BG_CONTENT,
            **kwargs
        )
        self.quiz_mgr = quiz_mgr

        self.current_screen = self.SCREEN_START
        self.selected_option_var = ctk.IntVar(value=-1)
        self.option_buttons = []
        self.quiz_timer_job = None
        self.elapsed_seconds = 0

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=24, pady=20)

        self._show_start_screen()

    def refresh(self) -> None:
        """Refreshes active view screen."""
        if self.current_screen == self.SCREEN_START:
            self._show_start_screen()
        elif self.current_screen == self.SCREEN_HISTORY:
            self._show_history_screen()

    # --------------------------------------------------------------------------
    # 1. START SCREEN
    # --------------------------------------------------------------------------
    def _show_start_screen(self) -> None:
        self.current_screen = self.SCREEN_START
        self._clear_container()

        # Title
        h1 = ctk.CTkLabel(self.container, text="Python & Data Science Quiz Zone", font=Theme.font_title(), text_color=Theme.TEXT_PRIMARY)
        h1.pack(anchor="w")

        sub = ctk.CTkLabel(
            self.container,
            text="Assess your Python fundamentals, OOP mastery, and NumPy knowledge with curated technical challenges.",
            font=Theme.font_body(),
            text_color=Theme.TEXT_MUTED
        )
        sub.pack(anchor="w", pady=(2, 20))

        # Main Setup Card
        card = ctk.CTkFrame(self.container, fg_color=Theme.BG_CARD, border_color=Theme.BORDER, border_width=1, corner_radius=12)
        card.pack(fill="x", pady=(0, 20))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=28, pady=24)

        ctk.CTkLabel(inner, text="⚙️ Configure Quiz Round", font=Theme.font_h2(), text_color=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 16))

        # Difficulty Selector
        ctk.CTkLabel(inner, text="Select Difficulty Level:", font=Theme.font_small_bold(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 4))
        self.diff_var = ctk.StringVar(value="All")
        self.diff_seg = ctk.CTkSegmentedButton(
            inner,
            values=["All", "Beginner", "Intermediate", "Advanced"],
            variable=self.diff_var,
            font=Theme.font_body_bold(),
            selected_color=Theme.ACCENT_PRIMARY
        )
        self.diff_seg.pack(anchor="w", pady=(0, 16))

        # Question Count Selector
        ctk.CTkLabel(inner, text="Number of Questions:", font=Theme.font_small_bold(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 4))
        self.count_var = ctk.StringVar(value="5")
        self.count_seg = ctk.CTkSegmentedButton(
            inner,
            values=["3", "5", "10"],
            variable=self.count_var,
            font=Theme.font_body_bold(),
            selected_color=Theme.ACCENT_PRIMARY
        )
        self.count_seg.pack(anchor="w", pady=(0, 24))

        # Start Button & History Button Row
        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.pack(fill="x")

        start_btn = ctk.CTkButton(
            btn_row,
            text="🚀 Begin Quiz",
            font=Theme.font_body_bold(),
            height=42,
            width=160,
            corner_radius=8,
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color=Theme.ACCENT_PRIMARY_HOVER,
            command=self._start_quiz_session
        )
        start_btn.pack(side="left", padx=(0, 12))

        hist_btn = ctk.CTkButton(
            btn_row,
            text="📜 Past Attempts",
            font=Theme.font_body(),
            height=42,
            width=140,
            corner_radius=8,
            fg_color=Theme.BG_SIDEBAR,
            hover_color=Theme.BG_CARD_HOVER,
            border_color=Theme.BORDER,
            border_width=1,
            command=self._show_history_screen
        )
        hist_btn.pack(side="left")

        # Quick Stats Preview Card
        past = self.quiz_mgr.get_past_attempts(limit=1)
        if past:
            last = past[0]
            tip_card = ctk.CTkFrame(self.container, fg_color=Theme.BG_CARD, corner_radius=8)
            tip_card.pack(fill="x")
            t_inner = ctk.CTkFrame(tip_card, fg_color="transparent")
            t_inner.pack(fill="x", padx=16, pady=12)

            ctk.CTkLabel(
                t_inner,
                text=f"Last Attempt: {last['score']}/{last['total_questions']} ({last['percentage']}%) — {last['difficulty']} Level • {last['completed_at'][:16]}",
                font=Theme.font_small_bold(),
                text_color=Theme.TEXT_ACCENT
            ).pack(side="left")

    # --------------------------------------------------------------------------
    # 2. ACTIVE QUIZ QUESTION SCREEN
    # --------------------------------------------------------------------------
    def _start_quiz_session(self) -> None:
        diff = self.diff_var.get()
        num_q = int(self.count_var.get())

        self.quiz_mgr.start_quiz(difficulty=diff, num_questions=num_q)
        self.elapsed_seconds = 0
        self.current_screen = self.SCREEN_QUIZ
        self._render_question_screen()
        self._schedule_quiz_timer()

    def _render_question_screen(self) -> None:
        self._clear_container()

        q = self.quiz_mgr.get_current_question()
        if not q:
            self._finish_and_show_results()
            return

        total_q = len(self.quiz_mgr.current_quiz)
        q_idx = self.quiz_mgr.current_index + 1

        # Header Info Bar: Question Counter + Tags + Live Timer
        top_bar = ctk.CTkFrame(self.container, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 14))

        count_lbl = ctk.CTkLabel(
            top_bar,
            text=f"Question {q_idx} of {total_q}",
            font=Theme.font_h2(),
            text_color=Theme.TEXT_PRIMARY
        )
        count_lbl.pack(side="left")

        # Topic & Difficulty Badges
        ctk.CTkLabel(
            top_bar,
            text=f" {q['topic']} ",
            font=Theme.font_small_bold(),
            fg_color=Theme.BG_CARD,
            text_color=Theme.ACCENT_PRIMARY,
            corner_radius=4
        ).pack(side="left", padx=(12, 6))

        ctk.CTkLabel(
            top_bar,
            text=f" {q['difficulty']} ",
            font=Theme.font_small_bold(),
            fg_color=Theme.BG_CARD,
            text_color=Theme.ACCENT_AMBER,
            corner_radius=4
        ).pack(side="left")

        # Live Elapsed Time
        self.timer_lbl = ctk.CTkLabel(
            top_bar,
            text=f"⏱️ {self._format_seconds(self.elapsed_seconds)}",
            font=Theme.font_body_bold(),
            text_color=Theme.TEXT_MUTED
        )
        self.timer_lbl.pack(side="right")

        # Progress bar
        pbar = ctk.CTkProgressBar(
            self.container,
            height=6,
            corner_radius=3,
            progress_color=Theme.ACCENT_PRIMARY,
            fg_color=Theme.BG_CARD
        )
        pbar.pack(fill="x", pady=(0, 20))
        pbar.set(q_idx / total_q)

        # Question Card
        q_card = ctk.CTkFrame(self.container, fg_color=Theme.BG_CARD, border_color=Theme.BORDER, border_width=1, corner_radius=10)
        q_card.pack(fill="x", pady=(0, 20))

        q_inner = ctk.CTkFrame(q_card, fg_color="transparent")
        q_inner.pack(fill="x", padx=24, pady=20)

        q_text = ctk.CTkLabel(
            q_inner,
            text=q["question"],
            font=Theme.font_h2(),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w",
            justify="left",
            wraplength=700
        )
        q_text.pack(anchor="w")

        # Options Container
        self.option_buttons = []
        user_saved_ans = self.quiz_mgr.user_answers[self.quiz_mgr.current_index]
        self.selected_option_var.set(user_saved_ans if user_saved_ans is not None else -1)

        for opt_idx, opt_text in enumerate(q["options"]):
            btn = ctk.CTkButton(
                self.container,
                text=f"{chr(65 + opt_idx)}.  {opt_text}",
                font=Theme.font_body(),
                height=48,
                corner_radius=8,
                anchor="w",
                fg_color=Theme.ACCENT_PRIMARY if self.selected_option_var.get() == opt_idx else Theme.BG_CARD,
                text_color="#FFFFFF" if self.selected_option_var.get() == opt_idx else Theme.TEXT_PRIMARY,
                hover_color=Theme.BG_CARD_HOVER,
                border_color=Theme.BORDER,
                border_width=1,
                command=lambda idx=opt_idx: self._select_option(idx)
            )
            btn.pack(fill="x", pady=5)
            self.option_buttons.append(btn)

        # Navigation Controls Row: Prev, Next / Finish
        nav_box = ctk.CTkFrame(self.container, fg_color="transparent")
        nav_box.pack(fill="x", pady=(24, 0))

        if self.quiz_mgr.current_index > 0:
            prev_btn = ctk.CTkButton(
                nav_box,
                text="← Previous",
                font=Theme.font_body(),
                width=110,
                height=38,
                fg_color=Theme.BG_CARD,
                hover_color=Theme.BG_CARD_HOVER,
                border_color=Theme.BORDER,
                border_width=1,
                command=self._prev_question
            )
            prev_btn.pack(side="left")

        is_last = (self.quiz_mgr.current_index == total_q - 1)
        next_text = "Finish Quiz 🏁" if is_last else "Next Question →"
        next_btn = ctk.CTkButton(
            nav_box,
            text=next_text,
            font=Theme.font_body_bold(),
            width=140,
            height=38,
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color=Theme.ACCENT_PRIMARY_HOVER,
            command=self._next_or_finish
        )
        next_btn.pack(side="right")

    def _select_option(self, opt_idx: int) -> None:
        self.selected_option_var.set(opt_idx)
        self.quiz_mgr.record_answer(opt_idx)

        # Update button highlights
        for i, btn in enumerate(self.option_buttons):
            if i == opt_idx:
                btn.configure(fg_color=Theme.ACCENT_PRIMARY, text_color="#FFFFFF")
            else:
                btn.configure(fg_color=Theme.BG_CARD, text_color=Theme.TEXT_PRIMARY)

    def _prev_question(self) -> None:
        self.quiz_mgr.previous_question()
        self._render_question_screen()

    def _next_or_finish(self) -> None:
        has_next = self.quiz_mgr.next_question()
        if has_next:
            self._render_question_screen()
        else:
            self._finish_and_show_results()

    def _schedule_quiz_timer(self) -> None:
        self.elapsed_seconds += 1
        if hasattr(self, "timer_lbl") and self.timer_lbl.winfo_exists():
            self.timer_lbl.configure(text=f"⏱️ {self._format_seconds(self.elapsed_seconds)}")
        self.quiz_timer_job = self.after(1000, self._schedule_quiz_timer)

    def _stop_quiz_timer(self) -> None:
        if self.quiz_timer_job:
            self.after_cancel(self.quiz_timer_job)
            self.quiz_timer_job = None

    def _format_seconds(self, secs: int) -> str:
        m = secs // 60
        s = secs % 60
        return f"{m:02d}:{s:02d}"

    # --------------------------------------------------------------------------
    # 3. RESULTS SCREEN
    # --------------------------------------------------------------------------
    def _finish_and_show_results(self) -> None:
        self._stop_quiz_timer()
        self.current_screen = self.SCREEN_RESULTS
        self._clear_container()

        results = self.quiz_mgr.finish_quiz()
        score = results["score"]
        total = results["total"]
        pct = results["percentage"]

        # Results Summary Card
        card = ctk.CTkFrame(self.container, fg_color=Theme.BG_CARD, border_color=Theme.BORDER, border_width=1, corner_radius=12)
        card.pack(fill="x", pady=(0, 20))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=24)

        if pct >= 80:
            status_text = "🎉 Outstanding Performance!"
            col = Theme.ACCENT_EMERALD
        elif pct >= 60:
            status_text = "👍 Good Job! Solid Understanding."
            col = Theme.ACCENT_PRIMARY
        else:
            status_text = "📚 Keep Practicing & Reviewing Concepts."
            col = Theme.ACCENT_AMBER

        ctk.CTkLabel(inner, text=status_text, font=Theme.font_h1(), text_color=col).pack(anchor="w")

        # Score Row
        score_row = ctk.CTkFrame(inner, fg_color="transparent")
        score_row.pack(anchor="w", pady=(8, 16))

        ctk.CTkLabel(
            score_row,
            text=f"{score} / {total}",
            font=Theme.font_stat_number(),
            text_color=Theme.TEXT_PRIMARY
        ).pack(side="left", padx=(0, 16))

        ctk.CTkLabel(
            score_row,
            text=f"Score: {pct:.0f}%  •  Time: {self._format_seconds(results['time_spent_seconds'])}",
            font=Theme.font_h2(),
            text_color=Theme.TEXT_ACCENT
        ).pack(side="left")

        # Action Buttons
        btn_box = ctk.CTkFrame(inner, fg_color="transparent")
        btn_box.pack(anchor="w")

        ctk.CTkButton(
            btn_box,
            text="🔄 Take Another Quiz",
            font=Theme.font_body_bold(),
            height=38,
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color=Theme.ACCENT_PRIMARY_HOVER,
            command=self._show_start_screen
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_box,
            text="📜 View Attempt History",
            font=Theme.font_body(),
            height=38,
            fg_color=Theme.BG_SIDEBAR,
            hover_color=Theme.BG_CARD_HOVER,
            border_color=Theme.BORDER,
            border_width=1,
            command=self._show_history_screen
        ).pack(side="left")

        # Breakdown Header
        ctk.CTkLabel(
            self.container,
            text="Detailed Question Review & Explanations",
            font=Theme.font_h2(),
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w", pady=(10, 8))

        # Each Question Explanation
        for idx, item in enumerate(results["breakdown"]):
            b_card = ctk.CTkFrame(self.container, fg_color=Theme.BG_CARD, border_color=Theme.BORDER, border_width=1, corner_radius=8)
            b_card.pack(fill="x", pady=6)

            b_inner = ctk.CTkFrame(b_card, fg_color="transparent")
            b_inner.pack(fill="x", padx=16, pady=12)

            # Icon + Question
            icon = "✅ Correct" if item["is_correct"] else "❌ Incorrect"
            i_col = Theme.ACCENT_EMERALD if item["is_correct"] else Theme.ACCENT_ROSE

            status_lbl = ctk.CTkLabel(b_inner, text=icon, font=Theme.font_small_bold(), text_color=i_col)
            status_lbl.pack(anchor="w")

            q_lbl = ctk.CTkLabel(b_inner, text=f"Q{idx + 1}: {item['question']}", font=Theme.font_body_bold(), text_color=Theme.TEXT_PRIMARY, wraplength=680, justify="left")
            q_lbl.pack(anchor="w", pady=(2, 6))

            # Options breakdown
            corr_opt = item["options"][item["correct_index"]]
            sel_opt = item["options"][item["selected_index"]] if item["selected_index"] is not None else "Skipped"

            ans_txt = f"Your Answer: {sel_opt}  |  Correct Answer: {corr_opt}"
            ctk.CTkLabel(b_inner, text=ans_txt, font=Theme.font_body(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w")

            # Explanation
            exp_box = ctk.CTkFrame(b_inner, fg_color=Theme.BG_SIDEBAR, corner_radius=6)
            exp_box.pack(fill="x", pady=(6, 0))
            ctk.CTkLabel(
                exp_box,
                text=f"💡 Explanation: {item['explanation']}",
                font=Theme.font_small(),
                text_color=Theme.TEXT_ACCENT,
                wraplength=660,
                justify="left"
            ).pack(anchor="w", padx=10, pady=8)

    # --------------------------------------------------------------------------
    # 4. HISTORY SCREEN
    # --------------------------------------------------------------------------
    def _show_history_screen(self) -> None:
        self.current_screen = self.SCREEN_HISTORY
        self._clear_container()

        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(header, text="📜 Quiz Attempt History", font=Theme.font_title(), text_color=Theme.TEXT_PRIMARY).pack(side="left")

        back_btn = ctk.CTkButton(
            header,
            text="← Back to Quiz",
            font=Theme.font_body_bold(),
            height=34,
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color=Theme.ACCENT_PRIMARY_HOVER,
            command=self._show_start_screen
        )
        back_btn.pack(side="right")

        history = self.quiz_mgr.get_past_attempts(limit=15)
        if not history:
            ctk.CTkLabel(
                self.container,
                text="No quiz attempts recorded yet.\nTake a quiz to see your score progression!",
                font=Theme.font_body(),
                text_color=Theme.TEXT_MUTED
            ).pack(pady=40)
            return

        card = ctk.CTkFrame(self.container, fg_color=Theme.BG_CARD, border_color=Theme.BORDER, border_width=1, corner_radius=10)
        card.pack(fill="x")

        # Table Header
        th = ctk.CTkFrame(card, fg_color=Theme.BG_SIDEBAR, corner_radius=6)
        th.pack(fill="x", padx=16, pady=(12, 6))

        ctk.CTkLabel(th, text="Topic", font=Theme.font_small_bold(), text_color=Theme.TEXT_MUTED, width=180, anchor="w").pack(side="left", padx=12, pady=6)
        ctk.CTkLabel(th, text="Difficulty", font=Theme.font_small_bold(), text_color=Theme.TEXT_MUTED, width=110, anchor="w").pack(side="left", padx=6, pady=6)
        ctk.CTkLabel(th, text="Score", font=Theme.font_small_bold(), text_color=Theme.TEXT_MUTED, width=80, anchor="w").pack(side="left", padx=6, pady=6)
        ctk.CTkLabel(th, text="Percentage", font=Theme.font_small_bold(), text_color=Theme.TEXT_MUTED, width=100, anchor="w").pack(side="left", padx=6, pady=6)
        ctk.CTkLabel(th, text="Time Spent", font=Theme.font_small_bold(), text_color=Theme.TEXT_MUTED, width=90, anchor="w").pack(side="left", padx=6, pady=6)
        ctk.CTkLabel(th, text="Completed At", font=Theme.font_small_bold(), text_color=Theme.TEXT_MUTED, anchor="e").pack(side="right", padx=12, pady=6)

        for a in history:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=2)

            ctk.CTkLabel(row, text=a["topic"], font=Theme.font_body_bold(), text_color=Theme.TEXT_PRIMARY, width=180, anchor="w").pack(side="left", padx=12, pady=4)
            ctk.CTkLabel(row, text=a["difficulty"], font=Theme.font_body(), text_color=Theme.TEXT_SECONDARY, width=110, anchor="w").pack(side="left", padx=6, pady=4)
            ctk.CTkLabel(row, text=f"{a['score']}/{a['total_questions']}", font=Theme.font_body_bold(), text_color=Theme.ACCENT_PRIMARY, width=80, anchor="w").pack(side="left", padx=6, pady=4)
            ctk.CTkLabel(row, text=f"{a['percentage']:.0f}%", font=Theme.font_body_bold(), text_color=Theme.ACCENT_EMERALD if a['percentage'] >= 70 else Theme.ACCENT_AMBER, width=100, anchor="w").pack(side="left", padx=6, pady=4)
            ctk.CTkLabel(row, text=self._format_seconds(a["time_spent_seconds"]), font=Theme.font_body(), text_color=Theme.TEXT_MUTED, width=90, anchor="w").pack(side="left", padx=6, pady=4)
            ctk.CTkLabel(row, text=a.get("completed_at", "")[:16], font=Theme.font_small(), text_color=Theme.TEXT_MUTED, anchor="e").pack(side="right", padx=12, pady=4)

    def _clear_container(self) -> None:
        self._stop_quiz_timer()
        for w in self.container.winfo_children():
            w.destroy()
