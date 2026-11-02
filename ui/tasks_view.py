"""
==============================================================================
StudySphere — Task Manager View & Task Modal
==============================================================================
Author: Senior Python Mentor & Architect
Role: Full CRUD task workspace with multi-criteria filtering (status,
      priority, subject), real-time search, deadline sorting, overdue badges,
      and an intuitive task editor dialog.
"""

from datetime import date, timedelta
import customtkinter as ctk
from tkinter import messagebox
from ui.theme import Theme
from modules.task_manager import TaskManager
from modules.subject_manager import SubjectManager


class TaskDialog(ctk.CTkToplevel):
    """
    Modal dialog window for creating or modifying a task.
    """

    def __init__(self, parent, task_mgr: TaskManager, subject_mgr: SubjectManager,
                 task_to_edit: dict = None, on_save_callback = None):
        super().__init__(parent)
        self.task_mgr = task_mgr
        self.subject_mgr = subject_mgr
        self.task_to_edit = task_to_edit
        self.on_save_callback = on_save_callback

        self.title("Edit Task" if task_to_edit else "Create New Task")
        self.geometry("540x620")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_CARD)
        self.transient(parent)
        self.grab_set()  # Modal lock

        self.subjects = self.subject_mgr.get_all_subjects()
        self.subject_map = {s["name"]: s["id"] for s in self.subjects}

        self._build_form()
        self._populate_fields()

    def _build_form(self) -> None:
        """Constructs form controls."""
        header_text = "✏️ Edit Academic Task" if self.task_to_edit else "✨ Create Academic Task"
        lbl = ctk.CTkLabel(self, text=header_text, font=Theme.font_h1(), text_color=Theme.TEXT_PRIMARY)
        lbl.pack(anchor="w", padx=24, pady=(20, 12))

        # Title Field
        t_lbl = ctk.CTkLabel(self, text="Task Title *", font=Theme.font_small_bold(), text_color=Theme.TEXT_SECONDARY)
        t_lbl.pack(anchor="w", padx=24, pady=(4, 2))
        self.title_entry = ctk.CTkEntry(
            self,
            placeholder_text="e.g. Implement Graph BFS & DFS in Python",
            font=Theme.font_body(),
            height=36,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER
        )
        self.title_entry.pack(fill="x", padx=24, pady=(0, 10))

        # Subject Dropdown
        sub_lbl = ctk.CTkLabel(self, text="Associated Subject", font=Theme.font_small_bold(), text_color=Theme.TEXT_SECONDARY)
        sub_lbl.pack(anchor="w", padx=24, pady=(4, 2))
        subject_options = ["None / General"] + list(self.subject_map.keys())
        self.subject_var = ctk.StringVar(value=subject_options[0])
        self.subject_menu = ctk.CTkOptionMenu(
            self,
            variable=self.subject_var,
            values=subject_options,
            font=Theme.font_body(),
            height=34,
            fg_color=Theme.BG_INPUT,
            button_color=Theme.ACCENT_PRIMARY,
            button_hover_color=Theme.ACCENT_PRIMARY_HOVER
        )
        self.subject_menu.pack(fill="x", padx=24, pady=(0, 10))

        # Priority & Status row
        row_opts = ctk.CTkFrame(self, fg_color="transparent")
        row_opts.pack(fill="x", padx=24, pady=(0, 10))
        row_opts.grid_columnconfigure((0, 1), weight=1)

        # Priority
        p_lbl = ctk.CTkLabel(row_opts, text="Priority", font=Theme.font_small_bold(), text_color=Theme.TEXT_SECONDARY)
        p_lbl.grid(row=0, column=0, sticky="w", pady=(0, 2))
        self.priority_var = ctk.StringVar(value="Medium")
        self.priority_menu = ctk.CTkOptionMenu(
            row_opts,
            variable=self.priority_var,
            values=["Low", "Medium", "High"],
            font=Theme.font_body(),
            height=34,
            fg_color=Theme.BG_INPUT,
            button_color=Theme.ACCENT_PRIMARY
        )
        self.priority_menu.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        # Status
        s_lbl = ctk.CTkLabel(row_opts, text="Status", font=Theme.font_small_bold(), text_color=Theme.TEXT_SECONDARY)
        s_lbl.grid(row=0, column=1, sticky="w", pady=(0, 2))
        self.status_var = ctk.StringVar(value="Pending")
        self.status_menu = ctk.CTkOptionMenu(
            row_opts,
            variable=self.status_var,
            values=["Pending", "In Progress", "Completed"],
            font=Theme.font_body(),
            height=34,
            fg_color=Theme.BG_INPUT,
            button_color=Theme.ACCENT_PRIMARY
        )
        self.status_menu.grid(row=1, column=1, sticky="ew", padx=(6, 0))

        # Due Date Field + Quick Date Buttons
        d_lbl = ctk.CTkLabel(self, text="Due Date (YYYY-MM-DD) *", font=Theme.font_small_bold(), text_color=Theme.TEXT_SECONDARY)
        d_lbl.pack(anchor="w", padx=24, pady=(4, 2))

        date_row = ctk.CTkFrame(self, fg_color="transparent")
        date_row.pack(fill="x", padx=24, pady=(0, 6))

        self.due_entry = ctk.CTkEntry(
            date_row,
            placeholder_text="2026-11-15",
            font=Theme.font_body(),
            height=34,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER
        )
        self.due_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        # Quick date shortcut buttons
        today = date.today()
        q_btns = [
            ("Today", today.isoformat()),
            ("Tmrw", (today + timedelta(days=1)).isoformat()),
            ("+3d", (today + timedelta(days=3)).isoformat()),
            ("+7d", (today + timedelta(days=7)).isoformat()),
        ]
        for label, val in q_btns:
            btn = ctk.CTkButton(
                date_row,
                text=label,
                font=Theme.font_small(),
                width=45,
                height=32,
                fg_color=Theme.BG_INPUT,
                hover_color=Theme.BG_CARD_HOVER,
                border_color=Theme.BORDER,
                border_width=1,
                command=lambda v=val: self._set_due_date(v)
            )
            btn.pack(side="left", padx=2)

        # Description Field
        desc_lbl = ctk.CTkLabel(self, text="Description / Lab Notes", font=Theme.font_small_bold(), text_color=Theme.TEXT_SECONDARY)
        desc_lbl.pack(anchor="w", padx=24, pady=(4, 2))
        self.desc_box = ctk.CTkTextbox(
            self,
            font=Theme.font_body(),
            height=90,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER,
            border_width=1
        )
        self.desc_box.pack(fill="x", padx=24, pady=(0, 12))

        # Error Message Label
        self.err_lbl = ctk.CTkLabel(self, text="", font=Theme.font_small_bold(), text_color=Theme.ACCENT_ROSE)
        self.err_lbl.pack(padx=24, pady=(0, 6))

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
            text="Save Task",
            font=Theme.font_body_bold(),
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color=Theme.ACCENT_PRIMARY_HOVER,
            command=self._handle_save
        )
        save_btn.pack(side="right")

    def _set_due_date(self, date_str: str) -> None:
        self.due_entry.delete(0, "end")
        self.due_entry.insert(0, date_str)

    def _populate_fields(self) -> None:
        """Fills form when editing an existing task."""
        if not self.task_to_edit:
            # Default to tomorrow
            self._set_due_date((date.today() + timedelta(days=1)).isoformat())
            return

        t = self.task_to_edit
        self.title_entry.insert(0, t.get("title", ""))
        self._set_due_date(t.get("due_date", ""))
        self.priority_var.set(t.get("priority", "Medium"))
        self.status_var.set(t.get("status", "Pending"))

        if t.get("subject_name") and t["subject_name"] in self.subject_map:
            self.subject_var.set(t["subject_name"])

        if t.get("description"):
            self.desc_box.insert("1.0", t["description"])

    def _handle_save(self) -> None:
        """Validates and executes task save or update."""
        title = self.title_entry.get()
        due_date = self.due_entry.get()
        priority = self.priority_var.get()
        status = self.status_var.get()
        desc = self.desc_box.get("1.0", "end-1c")

        sub_name = self.subject_var.get()
        subject_id = self.subject_map.get(sub_name)

        try:
            if self.task_to_edit:
                task_id = self.task_to_edit["id"]
                self.task_mgr.update_task(task_id, title, subject_id, priority, due_date, desc, status)
            else:
                self.task_mgr.add_task(title, subject_id, priority, due_date, desc, status)

            if self.on_save_callback:
                self.on_save_callback()

            self.destroy()
        except ValueError as e:
            self.err_lbl.configure(text=str(e))


class TasksView(ctk.CTkFrame):
    """
    Primary Task Manager dashboard screen.
    """

    def __init__(self, master, task_mgr: TaskManager, subject_mgr: SubjectManager, **kwargs):
        super().__init__(
            master,
            fg_color=Theme.BG_CONTENT,
            **kwargs
        )
        self.task_mgr = task_mgr
        self.subject_mgr = subject_mgr

        self._build_header()
        self._build_filters()
        self._build_task_list()
        self.refresh()

    def _build_header(self) -> None:
        """Renders title and 'New Task' button."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 12))

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left")

        h1 = ctk.CTkLabel(left, text="Task Management", font=Theme.font_title(), text_color=Theme.TEXT_PRIMARY)
        h1.pack(anchor="w")

        self.counter_lbl = ctk.CTkLabel(left, text="Showing 0 tasks", font=Theme.font_small(), text_color=Theme.TEXT_MUTED)
        self.counter_lbl.pack(anchor="w")

        add_btn = ctk.CTkButton(
            header,
            text="+ Add New Task",
            font=Theme.font_body_bold(),
            height=36,
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color=Theme.ACCENT_PRIMARY_HOVER,
            command=self._open_new_task_dialog
        )
        add_btn.pack(side="right")

    def _build_filters(self) -> None:
        """Renders search bar and filter dropdowns."""
        filter_bar = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, border_color=Theme.BORDER, border_width=1, corner_radius=8)
        filter_bar.pack(fill="x", padx=24, pady=(0, 14))

        # Search box
        self.search_entry = ctk.CTkEntry(
            filter_bar,
            placeholder_text="🔍 Search tasks by title or keywords...",
            font=Theme.font_body(),
            height=34,
            width=260,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER
        )
        self.search_entry.pack(side="left", padx=12, pady=10)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh())

        # Status filter
        self.status_filter_var = ctk.StringVar(value="All")
        status_menu = ctk.CTkOptionMenu(
            filter_bar,
            variable=self.status_filter_var,
            values=["All", "Pending", "In Progress", "Completed"],
            font=Theme.font_body(),
            width=110,
            height=34,
            fg_color=Theme.BG_INPUT,
            button_color=Theme.BG_SIDEBAR,
            command=lambda v: self.refresh()
        )
        status_menu.pack(side="left", padx=(0, 8), pady=10)

        # Priority filter
        self.priority_filter_var = ctk.StringVar(value="All")
        prio_menu = ctk.CTkOptionMenu(
            filter_bar,
            variable=self.priority_filter_var,
            values=["All", "High", "Medium", "Low"],
            font=Theme.font_body(),
            width=95,
            height=34,
            fg_color=Theme.BG_INPUT,
            button_color=Theme.BG_SIDEBAR,
            command=lambda v: self.refresh()
        )
        prio_menu.pack(side="left", padx=(0, 8), pady=10)

        # Sort Order
        self.sort_var = ctk.StringVar(value="Due Date")
        sort_menu = ctk.CTkOptionMenu(
            filter_bar,
            variable=self.sort_var,
            values=["Due Date", "Priority", "Newest"],
            font=Theme.font_body(),
            width=110,
            height=34,
            fg_color=Theme.BG_INPUT,
            button_color=Theme.BG_SIDEBAR,
            command=lambda v: self.refresh()
        )
        sort_menu.pack(side="right", padx=12, pady=10)

        sort_lbl = ctk.CTkLabel(filter_bar, text="Sort:", font=Theme.font_small_bold(), text_color=Theme.TEXT_MUTED)
        sort_lbl.pack(side="right", padx=(0, 4))

    def _build_task_list(self) -> None:
        """Constructs scrollable list container."""
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=24, pady=(0, 20))

    def refresh(self) -> None:
        """Fetches filtered tasks and re-renders items."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        status = self.status_filter_var.get()
        priority = self.priority_filter_var.get()
        search = self.search_entry.get()

        sort_map = {
            "Due Date": "due_date",
            "Priority": "priority",
            "Newest": "created_at"
        }
        sort_by = sort_map.get(self.sort_var.get(), "due_date")

        tasks = self.task_mgr.get_tasks(
            status=status,
            priority=priority,
            search_query=search,
            sort_by=sort_by
        )

        self.counter_lbl.configure(text=f"Showing {len(tasks)} tasks")

        if not tasks:
            empty_box = ctk.CTkFrame(self.scroll_frame, fg_color=Theme.BG_CARD, corner_radius=10)
            empty_box.pack(fill="x", pady=40)
            ctk.CTkLabel(
                empty_box,
                text="📋 No tasks match your criteria.\nCreate a new task or adjust your filters!",
                font=Theme.font_body(),
                text_color=Theme.TEXT_MUTED,
                justify="center"
            ).pack(pady=30)
            return

        for t in tasks:
            self._render_task_item(t)

    def _render_task_item(self, t: dict) -> None:
        """Renders an individual task card."""
        is_completed = (t["status"] == "Completed")

        card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=Theme.BG_CARD,
            border_color=Theme.BORDER if not t.get("is_overdue") else Theme.ACCENT_ROSE,
            border_width=1,
            corner_radius=8
        )
        card.pack(fill="x", pady=4)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=10)

        # Checkbox for toggle
        check_var = ctk.BooleanVar(value=is_completed)
        cb = ctk.CTkCheckBox(
            inner,
            text="",
            variable=check_var,
            width=24,
            checkbox_width=20,
            checkbox_height=20,
            corner_radius=4,
            fg_color=Theme.ACCENT_EMERALD,
            hover_color=Theme.ACCENT_PRIMARY_HOVER,
            command=lambda tid=t["id"]: self._toggle_status(tid)
        )
        cb.pack(side="left", padx=(0, 10))

        # Title & Subtitle
        text_col = ctk.CTkFrame(inner, fg_color="transparent")
        text_col.pack(side="left", fill="x", expand=True)

        title_color = Theme.TEXT_MUTED if is_completed else Theme.TEXT_PRIMARY
        title_font = Theme.font_body() if is_completed else Theme.font_body_bold()

        t_lbl = ctk.CTkLabel(text_col, text=t["title"], font=title_font, text_color=title_color, anchor="w")
        t_lbl.pack(anchor="w")

        # Details row under title
        details_row = ctk.CTkFrame(text_col, fg_color="transparent")
        details_row.pack(anchor="w", pady=(2, 0))

        # Subject pill
        course_name = t["subject_code"] or "General"
        sub_color = t["subject_color"] or Theme.ACCENT_PRIMARY
        ctk.CTkLabel(
            details_row,
            text=f" {course_name} ",
            font=Theme.font_small_bold(),
            fg_color=Theme.BG_SIDEBAR,
            text_color=sub_color,
            corner_radius=4
        ).pack(side="left", padx=(0, 6))

        # Priority pill
        prio = t["priority"]
        prio_color = Theme.ACCENT_ROSE if prio == "High" else (Theme.ACCENT_AMBER if prio == "Medium" else Theme.ACCENT_BLUE)
        ctk.CTkLabel(
            details_row,
            text=f" {prio} ",
            font=Theme.font_small_bold(),
            fg_color=Theme.BG_SIDEBAR,
            text_color=prio_color,
            corner_radius=4
        ).pack(side="left", padx=(0, 6))

        # Due Date / Overdue badge
        if t.get("is_overdue"):
            due_badge = ctk.CTkLabel(
                details_row,
                text=f" ⚠️ Overdue ({t['due_date']}) ",
                font=Theme.font_small_bold(),
                fg_color=Theme.ACCENT_ROSE,
                text_color="#FFFFFF",
                corner_radius=4
            )
            due_badge.pack(side="left")
        else:
            days = t.get("days_remaining", 0)
            if days == 0:
                due_text = "📅 Due Today"
                d_color = Theme.ACCENT_AMBER
            elif days == 1:
                due_text = "📅 Due Tomorrow"
                d_color = Theme.TEXT_ACCENT
            else:
                due_text = f"📅 Due: {t['due_date']}"
                d_color = Theme.TEXT_MUTED

            ctk.CTkLabel(
                details_row,
                text=due_text,
                font=Theme.font_small(),
                text_color=d_color
            ).pack(side="left")

        # Right Action Buttons (Edit & Delete)
        act_box = ctk.CTkFrame(inner, fg_color="transparent")
        act_box.pack(side="right")

        edit_btn = ctk.CTkButton(
            act_box,
            text="✏️",
            width=30,
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_SIDEBAR,
            hover_color=Theme.BG_CARD_HOVER,
            command=lambda task=t: self._open_edit_task_dialog(task)
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
            command=lambda tid=t["id"]: self._delete_task(tid)
        )
        del_btn.pack(side="left", padx=2)

    def _toggle_status(self, task_id: int) -> None:
        self.task_mgr.toggle_task_status(task_id)
        self.refresh()

    def _delete_task(self, task_id: int) -> None:
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to permanently delete this task?"):
            self.task_mgr.delete_task(task_id)
            self.refresh()

    def _open_new_task_dialog(self) -> None:
        TaskDialog(self, self.task_mgr, self.subject_mgr, on_save_callback=self.refresh)

    def _open_edit_task_dialog(self, task: dict) -> None:
        TaskDialog(self, self.task_mgr, self.subject_mgr, task_to_edit=task, on_save_callback=self.refresh)
