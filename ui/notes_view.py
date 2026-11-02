"""
==============================================================================
StudySphere — Notes Manager View
==============================================================================
Author: Senior Python Mentor & Architect
Role: Split-view note-taking workspace. Real-time search across titles & bodies,
      subject categorization, tags, and persistent CRUD operations in SQLite.
"""

import customtkinter as ctk
from tkinter import messagebox
from ui.theme import Theme
from modules.notes import NotesManager
from modules.subject_manager import SubjectManager


class NotesView(ctk.CTkFrame):
    """
    Split-view notes workspace.
    """

    def __init__(self, master, notes_mgr: NotesManager, subject_mgr: SubjectManager, **kwargs):
        super().__init__(
            master,
            fg_color=Theme.BG_CONTENT,
            **kwargs
        )
        self.notes_mgr = notes_mgr
        self.subject_mgr = subject_mgr

        self.current_note_id = None
        self.subjects = []
        self.subject_map = {}

        self._build_layout()
        self.refresh()

    def _build_layout(self) -> None:
        """Constructs split-view grid layout."""
        self.grid_columnconfigure(0, weight=2, minsize=280) # Left List Pane
        self.grid_columnconfigure(1, weight=5, minsize=420) # Right Editor Pane
        self.grid_rowconfigure(0, weight=1)

        # ----------------------------------------------------------------------
        # LEFT PANE: Note Search & List
        # ----------------------------------------------------------------------
        left_frame = ctk.CTkFrame(self, fg_color=Theme.BG_SIDEBAR, border_color=Theme.BORDER, border_width=1, corner_radius=0)
        left_frame.grid(row=0, column=0, sticky="nsew")

        # Top Bar in Left Pane
        top_box = ctk.CTkFrame(left_frame, fg_color="transparent")
        top_box.pack(fill="x", padx=16, pady=(18, 12))

        ctk.CTkLabel(top_box, text="Study Notes", font=Theme.font_h2(), text_color=Theme.TEXT_PRIMARY).pack(side="left")

        new_btn = ctk.CTkButton(
            top_box,
            text="+ New",
            font=Theme.font_small_bold(),
            width=65,
            height=28,
            corner_radius=6,
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color=Theme.ACCENT_PRIMARY_HOVER,
            command=self._create_new_note
        )
        new_btn.pack(side="right")

        # Search Box
        self.search_entry = ctk.CTkEntry(
            left_frame,
            placeholder_text="🔍 Search notes...",
            font=Theme.font_body(),
            height=32,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER
        )
        self.search_entry.pack(fill="x", padx=16, pady=(0, 8))
        self.search_entry.bind("<KeyRelease>", lambda e: self._populate_notes_list())

        # Subject Filter Menu
        self.sub_filter_var = ctk.StringVar(value="All Subjects")
        self.sub_filter_menu = ctk.CTkOptionMenu(
            left_frame,
            variable=self.sub_filter_var,
            values=["All Subjects"],
            font=Theme.font_body(),
            height=30,
            fg_color=Theme.BG_INPUT,
            button_color=Theme.BG_SIDEBAR,
            command=lambda v: self._populate_notes_list()
        )
        self.sub_filter_menu.pack(fill="x", padx=16, pady=(0, 10))

        # Scrollable Notes List
        self.list_scroll = ctk.CTkScrollableFrame(left_frame, fg_color="transparent")
        self.list_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 12))

        # ----------------------------------------------------------------------
        # RIGHT PANE: Note Editor
        # ----------------------------------------------------------------------
        self.right_frame = ctk.CTkFrame(self, fg_color=Theme.BG_CONTENT, corner_radius=0)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Editor Header: Note Title + Subject Selector
        ed_head = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        ed_head.pack(fill="x", pady=(0, 10))

        self.title_entry = ctk.CTkEntry(
            ed_head,
            placeholder_text="Note Title...",
            font=Theme.font_title(),
            height=42,
            fg_color=Theme.BG_CARD,
            border_color=Theme.BORDER
        )
        self.title_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.editor_subject_var = ctk.StringVar(value="No Subject")
        self.editor_sub_menu = ctk.CTkOptionMenu(
            ed_head,
            variable=self.editor_subject_var,
            values=["No Subject"],
            font=Theme.font_body(),
            height=40,
            width=160,
            fg_color=Theme.BG_CARD,
            button_color=Theme.ACCENT_PRIMARY
        )
        self.editor_sub_menu.pack(side="right")

        # Tags Entry
        self.tags_entry = ctk.CTkEntry(
            self.right_frame,
            placeholder_text="🏷️ Tags (comma-separated, e.g. python, algorithms, formulas)",
            font=Theme.font_small(),
            height=30,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER
        )
        self.tags_entry.pack(fill="x", pady=(0, 12))

        # Content Textbox
        self.content_box = ctk.CTkTextbox(
            self.right_frame,
            font=Theme.font_body(),
            fg_color=Theme.BG_CARD,
            border_color=Theme.BORDER,
            border_width=1,
            wrap="word"
        )
        self.content_box.pack(fill="both", expand=True, pady=(0, 14))

        # Action Bar: Delete, Clear, Save
        act_bar = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        act_bar.pack(fill="x")

        self.del_btn = ctk.CTkButton(
            act_bar,
            text="🗑️ Delete Note",
            font=Theme.font_body(),
            height=36,
            fg_color=Theme.BG_CARD,
            hover_color="#451A24",
            text_color=Theme.ACCENT_ROSE,
            command=self._delete_current_note
        )
        self.del_btn.pack(side="left")

        self.save_btn = ctk.CTkButton(
            act_bar,
            text="💾 Save Changes",
            font=Theme.font_body_bold(),
            height=36,
            width=130,
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color=Theme.ACCENT_PRIMARY_HOVER,
            command=self._save_note
        )
        self.save_btn.pack(side="right")

    def refresh(self) -> None:
        """Refreshes subject options and notes list."""
        self.subjects = self.subject_mgr.get_all_subjects()
        self.subject_map = {s["name"]: s["id"] for s in self.subjects}

        # Update filters
        filter_vals = ["All Subjects"] + list(self.subject_map.keys())
        self.sub_filter_menu.configure(values=filter_vals)

        ed_vals = ["No Subject"] + list(self.subject_map.keys())
        self.editor_sub_menu.configure(values=ed_vals)

        self._populate_notes_list()

    def _populate_notes_list(self) -> None:
        """Renders notes in the scrollable left list."""
        for w in self.list_scroll.winfo_children():
            w.destroy()

        sub_choice = self.sub_filter_var.get()
        sub_id = self.subject_map.get(sub_choice) if sub_choice != "All Subjects" else None
        search = self.search_entry.get().strip()

        notes = self.notes_mgr.get_notes(subject_id=sub_id, search_query=search)

        if not notes:
            ctk.CTkLabel(
                self.list_scroll,
                text="No notes found.\nClick '+ New' to create one!",
                font=Theme.font_small(),
                text_color=Theme.TEXT_MUTED
            ).pack(pady=30)
            return

        for n in notes:
            is_active = (n["id"] == self.current_note_id)

            card = ctk.CTkFrame(
                self.list_scroll,
                height=64,
                corner_radius=6,
                fg_color=Theme.BG_CARD_HOVER if is_active else Theme.BG_CARD,
                border_color=Theme.ACCENT_PRIMARY if is_active else Theme.BORDER,
                border_width=1
            )
            card.pack(fill="x", pady=3)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=10, pady=6)

            title_lbl = ctk.CTkLabel(
                inner,
                text=n["title"][:28] + ("..." if len(n["title"]) > 28 else ""),
                font=Theme.font_body_bold(),
                text_color=Theme.TEXT_PRIMARY,
                anchor="w"
            )
            title_lbl.pack(anchor="w")

            sub_text = n.get("subject_code") or "General"
            time_str = n.get("updated_at", "")[:10]
            foot_lbl = ctk.CTkLabel(
                inner,
                text=f"{sub_text} • {time_str}",
                font=Theme.font_small(),
                text_color=Theme.TEXT_MUTED,
                anchor="w"
            )
            foot_lbl.pack(anchor="w")

            # Bind click event on card and labels to select note
            for w in (card, inner, title_lbl, foot_lbl):
                w.bind("<Button-1>", lambda e, nid=n["id"]: self._load_note(nid))

    def _create_new_note(self) -> None:
        """Clears editor for creating a new note."""
        self.current_note_id = None
        self.title_entry.delete(0, "end")
        self.tags_entry.delete(0, "end")
        self.content_box.delete("1.0", "end")
        self.editor_subject_var.set("No Subject")
        self.del_btn.configure(state="disabled")
        self._populate_notes_list()

    def _load_note(self, note_id: int) -> None:
        """Loads selected note into the editor pane."""
        note = self.notes_mgr.get_note_by_id(note_id)
        if not note:
            return

        self.current_note_id = note["id"]
        self.del_btn.configure(state="normal")

        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, note["title"])

        self.tags_entry.delete(0, "end")
        if note.get("tags"):
            self.tags_entry.insert(0, note["tags"])

        self.content_box.delete("1.0", "end")
        self.content_box.insert("1.0", note["content"])

        if note.get("subject_name") and note["subject_name"] in self.subject_map:
            self.editor_subject_var.set(note["subject_name"])
        else:
            self.editor_subject_var.set("No Subject")

        self._populate_notes_list()

    def _save_note(self) -> None:
        """Validates and saves the active note."""
        title = self.title_entry.get().strip()
        tags = self.tags_entry.get().strip()
        content = self.content_box.get("1.0", "end-1c").strip()

        if not title:
            messagebox.showwarning("Incomplete Note", "Please provide a title for your note.")
            return

        if not content:
            messagebox.showwarning("Incomplete Note", "Note content cannot be empty.")
            return

        sub_choice = self.editor_subject_var.get()
        subject_id = self.subject_map.get(sub_choice)

        try:
            if self.current_note_id:
                self.notes_mgr.update_note(self.current_note_id, title, content, subject_id, tags)
            else:
                self.current_note_id = self.notes_mgr.add_note(title, content, subject_id, tags)
                self.del_btn.configure(state="normal")

            self._populate_notes_list()
            messagebox.showinfo("Saved", "Note saved successfully!")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _delete_current_note(self) -> None:
        if not self.current_note_id:
            return

        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this note?"):
            self.notes_mgr.delete_note(self.current_note_id)
            self._create_new_note()
