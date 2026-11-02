"""
==============================================================================
StudySphere — Subject Manager View & Subject Modal
==============================================================================
Author: Senior Python Mentor & Architect
Role: Full CRUD workspace for academic courses and subjects, displaying
      aggregated task statistics, course hours, and progress bars.
"""

import customtkinter as ctk
from tkinter import messagebox
from ui.theme import Theme
from modules.subject_manager import SubjectManager


class SubjectDialog(ctk.CTkToplevel):
    """
    Modal dialog window for creating or editing an academic subject.
    """

    def __init__(self, parent, subject_mgr: SubjectManager,
                 subject_to_edit: dict = None, on_save_callback = None):
        super().__init__(parent)
        self.subject_mgr = subject_mgr
        self.subject_to_edit = subject_to_edit
        self.on_save_callback = on_save_callback

        self.title("Edit Subject" if subject_to_edit else "Add New Subject")
        self.geometry("480x520")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_CARD)
        self.transient(parent)
        self.grab_set()

        self.selected_color = "#8B5CF6"
        self.color_buttons = []

        self._build_form()
        self._populate_fields()

    def _build_form(self) -> None:
        """Builds dialog form fields."""
        header_text = "✏️ Edit Academic Subject" if self.task_to_edit_check() else "📚 Add Academic Subject"
        lbl = ctk.CTkLabel(self, text=header_text, font=Theme.font_h1(), text_color=Theme.TEXT_PRIMARY)
        lbl.pack(anchor="w", padx=24, pady=(20, 12))

        # Subject Name
        n_lbl = ctk.CTkLabel(self, text="Course Name *", font=Theme.font_small_bold(), text_color=Theme.TEXT_SECONDARY)
        n_lbl.pack(anchor="w", padx=24, pady=(4, 2))
        self.name_entry = ctk.CTkEntry(
            self,
            placeholder_text="e.g. Machine Learning & Pattern Recognition",
            font=Theme.font_body(),
            height=36,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER
        )
        self.name_entry.pack(fill="x", padx=24, pady=(0, 10))

        # Course Code
        c_lbl = ctk.CTkLabel(self, text="Course Code *", font=Theme.font_small_bold(), text_color=Theme.TEXT_SECONDARY)
        c_lbl.pack(anchor="w", padx=24, pady=(4, 2))
        self.code_entry = ctk.CTkEntry(
            self,
            placeholder_text="e.g. CS204",
            font=Theme.font_body(),
            height=36,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER
        )
        self.code_entry.pack(fill="x", padx=24, pady=(0, 10))

        # Color Tag Selector
        col_lbl = ctk.CTkLabel(self, text="Accent Color Tag", font=Theme.font_small_bold(), text_color=Theme.TEXT_SECONDARY)
        col_lbl.pack(anchor="w", padx=24, pady=(4, 4))

        color_row = ctk.CTkFrame(self, fg_color="transparent")
        color_row.pack(anchor="w", padx=24, pady=(0, 12))

        for color_hex in SubjectManager.DEFAULT_COLORS:
            btn = ctk.CTkButton(
                color_row,
                text="",
                width=28,
                height=28,
                corner_radius=14,
                fg_color=color_hex,
                hover_color=color_hex,
                border_width=2,
                border_color="#FFFFFF" if color_hex == self.selected_color else "transparent",
                command=lambda c=color_hex: self._select_color(c)
            )
            btn.pack(side="left", padx=4)
            self.color_buttons.append((btn, color_hex))

        # Description
        d_lbl = ctk.CTkLabel(self, text="Course Description", font=Theme.font_small_bold(), text_color=Theme.TEXT_SECONDARY)
        d_lbl.pack(anchor="w", padx=24, pady=(4, 2))
        self.desc_box = ctk.CTkTextbox(
            self,
            font=Theme.font_body(),
            height=90,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER,
            border_width=1
        )
        self.desc_box.pack(fill="x", padx=24, pady=(0, 12))

        # Error Label
        self.err_lbl = ctk.CTkLabel(self, text="", font=Theme.font_small_bold(), text_color=Theme.ACCENT_ROSE)
        self.err_lbl.pack(padx=24, pady=(0, 8))

        # Action Buttons
        btn_box = ctk.CTkFrame(self, fg_color="transparent")
        btn_box.pack(fill="x", padx=24, pady=(0, 20))

        cancel_btn = ctk.CTkButton(
            btn_box,
            text="Cancel",
            font=Theme.font_body(),
            fg_color="transparent",
            hover_color=Theme.BG_CARD_HOVER,
            text_color=Theme.TEXT_MUTED,
            command=self.destroy
        )
        cancel_btn.pack(side="left")

        save_btn = ctk.CTkButton(
            btn_box,
            text="Save Subject",
            font=Theme.font_body_bold(),
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color=Theme.ACCENT_PRIMARY_HOVER,
            command=self._handle_save
        )
        save_btn.pack(side="right")

    def task_to_edit_check(self) -> bool:
        return self.subject_to_edit is not None

    def _select_color(self, color_hex: str) -> None:
        self.selected_color = color_hex
        for btn, c in self.color_buttons:
            if c == color_hex:
                btn.configure(border_color="#FFFFFF")
            else:
                btn.configure(border_color="transparent")

    def _populate_fields(self) -> None:
        if not self.subject_to_edit:
            return
        s = self.subject_to_edit
        self.name_entry.insert(0, s.get("name", ""))
        self.code_entry.insert(0, s.get("code", ""))
        if s.get("description"):
            self.desc_box.insert("1.0", s["description"])
        if s.get("color"):
            self._select_color(s["color"])

    def _handle_save(self) -> None:
        name = self.name_entry.get()
        code = self.code_entry.get()
        desc = self.desc_box.get("1.0", "end-1c")

        try:
            if self.subject_to_edit:
                sub_id = self.subject_to_edit["id"]
                self.subject_mgr.update_subject(sub_id, name, code, self.selected_color, desc)
            else:
                self.subject_mgr.add_subject(name, code, self.selected_color, desc)

            if self.on_save_callback:
                self.on_save_callback()

            self.destroy()
        except ValueError as e:
            self.err_lbl.configure(text=str(e))


class SubjectsView(ctk.CTkFrame):
    """
    Subjects & Coursework management view.
    """

    def __init__(self, master, subject_mgr: SubjectManager, on_view_subject_tasks, **kwargs):
        super().__init__(
            master,
            fg_color=Theme.BG_CONTENT,
            **kwargs
        )
        self.subject_mgr = subject_mgr
        self.on_view_subject_tasks = on_view_subject_tasks

        self._build_header()
        self._build_container()
        self.refresh()

    def _build_header(self) -> None:
        """Header with title and Add Subject action."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 16))

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left")

        h1 = ctk.CTkLabel(left, text="Academic Subjects", font=Theme.font_title(), text_color=Theme.TEXT_PRIMARY)
        h1.pack(anchor="w")

        sub = ctk.CTkLabel(
            left,
            text="Manage enrolled subjects, review task completion rates, and track study time.",
            font=Theme.font_body(),
            text_color=Theme.TEXT_MUTED
        )
        sub.pack(anchor="w")

        add_btn = ctk.CTkButton(
            header,
            text="+ Add Subject",
            font=Theme.font_body_bold(),
            height=36,
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color=Theme.ACCENT_PRIMARY_HOVER,
            command=self._open_new_subject_dialog
        )
        add_btn.pack(side="right")

    def _build_container(self) -> None:
        """Scrollable container for subjects."""
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=24, pady=(0, 20))

    def refresh(self) -> None:
        """Refreshes subject cards from database."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        subjects = self.subject_mgr.get_subjects_with_task_counts()

        if not subjects:
            empty_box = ctk.CTkFrame(self.scroll_frame, fg_color=Theme.BG_CARD, corner_radius=10)
            empty_box.pack(fill="x", pady=40)
            ctk.CTkLabel(
                empty_box,
                text="📚 No academic subjects registered yet.\nClick '+ Add Subject' to begin organizing your curriculum!",
                font=Theme.font_body(),
                text_color=Theme.TEXT_MUTED,
                justify="center"
            ).pack(pady=30)
            return

        for s in subjects:
            self._render_subject_card(s)

    def _render_subject_card(self, s: dict) -> None:
        """Renders an individual subject card."""
        card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=Theme.BG_CARD,
            border_color=Theme.BORDER,
            border_width=1,
            corner_radius=10
        )
        card.pack(fill="x", pady=6)

        # Top Accent Color Bar
        color_bar = ctk.CTkFrame(card, height=4, fg_color=s["color"], corner_radius=0)
        color_bar.pack(fill="x")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=18, pady=14)

        # Header Row: Code Pill + Subject Name + Action Buttons
        top_row = ctk.CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x")

        code_pill = ctk.CTkLabel(
            top_row,
            text=f" {s['code']} ",
            font=Theme.font_small_bold(),
            fg_color=s["color"],
            text_color="#FFFFFF",
            corner_radius=4
        )
        code_pill.pack(side="left", padx=(0, 10))

        name_lbl = ctk.CTkLabel(
            top_row,
            text=s["name"],
            font=Theme.font_h2(),
            text_color=Theme.TEXT_PRIMARY
        )
        name_lbl.pack(side="left")

        # Edit & Delete Buttons
        act_box = ctk.CTkFrame(top_row, fg_color="transparent")
        act_box.pack(side="right")

        edit_btn = ctk.CTkButton(
            act_box,
            text="✏️",
            width=30,
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_SIDEBAR,
            hover_color=Theme.BG_CARD_HOVER,
            command=lambda sub=s: self._open_edit_subject_dialog(sub)
        )
        edit_btn.pack(side="left", padx=2)

        del_btn = ctk.CTkButton(
            act_box,
            text="🗑️",
            width=30,
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_SIDEBAR,
            hover_color="#451A24",
            text_color=Theme.ACCENT_ROSE,
            command=lambda sid=s["id"]: self._delete_subject(sid)
        )
        del_btn.pack(side="left", padx=2)

        # Description if present
        if s.get("description"):
            desc_lbl = ctk.CTkLabel(
                inner,
                text=s["description"],
                font=Theme.font_body(),
                text_color=Theme.TEXT_MUTED,
                anchor="w",
                justify="left"
            )
            desc_lbl.pack(anchor="w", pady=(6, 8))

        # Metrics Strip
        metrics_row = ctk.CTkFrame(inner, fg_color=Theme.BG_SIDEBAR, corner_radius=6)
        metrics_row.pack(fill="x", pady=(4, 8))

        m_inner = ctk.CTkFrame(metrics_row, fg_color="transparent")
        m_inner.pack(fill="x", padx=12, pady=6)

        tot_txt = f"Total Tasks: {s['total_tasks']}"
        pend_txt = f"Pending: {s['pending_tasks']}"
        comp_txt = f"Completed: {s['completed_tasks']}"
        hrs_txt = f"Study Logged: {s['study_hours']}h"

        for label_text in (tot_txt, pend_txt, comp_txt, hrs_txt):
            ctk.CTkLabel(
                m_inner,
                text=label_text,
                font=Theme.font_small_bold(),
                text_color=Theme.TEXT_SECONDARY
            ).pack(side="left", padx=(0, 16))

        # Progress Bar for Completion Rate
        rate = s.get("completion_rate", 0.0)
        p_row = ctk.CTkFrame(inner, fg_color="transparent")
        p_row.pack(fill="x", pady=(2, 0))

        rate_lbl = ctk.CTkLabel(
            p_row,
            text=f"Completion: {rate:.0f}%",
            font=Theme.font_small(),
            text_color=Theme.TEXT_ACCENT
        )
        rate_lbl.pack(side="left", padx=(0, 8))

        pbar = ctk.CTkProgressBar(
            p_row,
            height=8,
            corner_radius=4,
            progress_color=s["color"],
            fg_color=Theme.BORDER
        )
        pbar.pack(side="left", fill="x", expand=True)
        pbar.set(rate / 100.0)

    def _delete_subject(self, subject_id: int) -> None:
        if messagebox.askyesno(
            "Confirm Subject Deletion",
            "Are you sure? Tasks and notes associated with this subject will be retained as unassigned."
        ):
            self.subject_mgr.delete_subject(subject_id)
            self.refresh()

    def _open_new_subject_dialog(self) -> None:
        SubjectDialog(self, self.subject_mgr, on_save_callback=self.refresh)

    def _open_edit_subject_dialog(self, subject: dict) -> None:
        SubjectDialog(self, self.subject_mgr, subject_to_edit=subject, on_save_callback=self.refresh)
