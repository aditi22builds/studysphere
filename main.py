"""
==============================================================================
StudySphere — Your Personal Student Command Center
==============================================================================
Author: Senior Python Mentor & Architect
Portfolio: 2nd-Year B.Tech Computer Science & Engineering (Data Science)
Role: Main Application Entry Point & Controller coordinating the GUI,
      SQLite database, business logic modules, and view routing.

Python & Software Engineering Concepts Demonstrated:
1. Object-Oriented Architecture & Inheritance (ctk.CTk master window subclass)
2. Model-View-Controller (MVC) Separation of Concerns:
   - Model: DatabaseManager, SQLite relational tables
   - Controller: Domain services (TaskManager, SubjectManager, FocusTimer, etc.)
   - View: CustomTkinter components, embedded Matplotlib figures
3. Non-Blocking Event Loops (Pomodoro timing via after() callback scheduling)
4. Data Science Integration (NumPy statistical calculations, Matplotlib data viz)
5. Parameterized SQL & Foreign Key Constraints (SQLite 3)
6. Robust Input Validation (Regex pattern matching for ISO dates & hex codes)
==============================================================================
"""

import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

# Ensure the studysphere package directory is on the Python path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Import Design Tokens
from ui.theme import Theme

# Import Database & Business Modules
from database.db_manager import DatabaseManager
from modules.task_manager import TaskManager
from modules.subject_manager import SubjectManager
from modules.focus_timer import FocusTimer
from modules.analytics import AnalyticsEngine
from modules.quiz import QuizManager
from modules.notes import NotesManager
from modules.notifications import NotificationManager

# Import UI Views & Components
from ui.sidebar import Sidebar
from ui.topbar import Topbar
from ui.dashboard import DashboardView
from ui.tasks_view import TasksView, TaskDialog
from ui.subjects_view import SubjectsView
from ui.timer_view import TimerView
from ui.analytics_view import AnalyticsView
from ui.quiz_view import QuizView
from ui.notes_view import NotesView
from ui.notifications_view import NotificationsView


class StudySphereApp(ctk.CTk):
    """
    Main Application Window and central state controller for StudySphere.
    """

    def __init__(self):
        super().__init__()

        # Window Appearance & Configuration
        self.title("StudySphere — Your Personal Student Command Center")
        self.geometry("1280x820")
        self.minsize(1040, 680)
        self.configure(fg_color=Theme.BG_WINDOW)

        # 1. Initialize Database & Service Layer
        self.db = DatabaseManager()
        self.subject_mgr = SubjectManager(self.db)
        self.task_mgr = TaskManager(self.db)
        self.timer_mgr = FocusTimer(self.db)
        self.analytics_mgr = AnalyticsEngine(self.db)
        self.quiz_mgr = QuizManager(self.db)
        self.notes_mgr = NotesManager(self.db)
        self.notif_mgr = NotificationManager(self.db)

        # 2. Build Master Layout Shell
        self._build_shell()

        # 3. Initialize Views
        self._initialize_views()

        # 4. Route to Default View
        self.show_view("dashboard")

        # 5. Refresh Notification Badges
        self._refresh_notification_badges()

    def _build_shell(self) -> None:
        """Constructs the master layout: Sidebar on the left, Main content on the right."""
        # Configure Root Grid
        self.grid_columnconfigure(0, weight=0) # Fixed-width sidebar
        self.grid_columnconfigure(1, weight=1) # Fluid main content area
        self.grid_rowconfigure(0, weight=1)

        # Left Sidebar Component
        self.sidebar = Sidebar(
            self,
            on_navigate=self.show_view,
            on_load_demo=self._handle_load_demo_data,
            on_clear_data=self._handle_clear_data
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Right Content Container
        self.main_container = ctk.CTkFrame(self, fg_color=Theme.BG_CONTENT, corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=0) # Topbar
        self.main_container.grid_rowconfigure(1, weight=1) # View Frame
        self.main_container.grid_columnconfigure(0, weight=1)

        # Topbar Component
        self.topbar = Topbar(
            self.main_container,
            on_quick_task=self._open_quick_task,
            on_quick_timer=lambda: self.show_view("timer"),
            on_view_notifications=lambda: self.show_view("notifications")
        )
        self.topbar.grid(row=0, column=0, sticky="ew")

        # Content Viewport (where views are swapped)
        self.viewport = ctk.CTkFrame(self.main_container, fg_color="transparent", corner_radius=0)
        self.viewport.grid(row=1, column=0, sticky="nsew")
        self.viewport.grid_rowconfigure(0, weight=1)
        self.viewport.grid_columnconfigure(0, weight=1)

    def _initialize_views(self) -> None:
        """Pre-instantiates all application views for instant switching."""
        self.views = {}

        self.views["dashboard"] = DashboardView(
            self.viewport,
            task_mgr=self.task_mgr,
            subject_mgr=self.subject_mgr,
            timer_mgr=self.timer_mgr,
            analytics_mgr=self.analytics_mgr,
            on_navigate=self.show_view
        )

        self.views["tasks"] = TasksView(
            self.viewport,
            task_mgr=self.task_mgr,
            subject_mgr=self.subject_mgr
        )

        self.views["subjects"] = SubjectsView(
            self.viewport,
            subject_mgr=self.subject_mgr,
            on_view_subject_tasks=lambda: self.show_view("tasks")
        )

        self.views["timer"] = TimerView(
            self.viewport,
            timer_mgr=self.timer_mgr,
            subject_mgr=self.subject_mgr
        )

        self.views["analytics"] = AnalyticsView(
            self.viewport,
            analytics_mgr=self.analytics_mgr,
            timer_mgr=self.timer_mgr
        )

        self.views["quiz"] = QuizView(
            self.viewport,
            quiz_mgr=self.quiz_mgr
        )

        self.views["notes"] = NotesView(
            self.viewport,
            notes_mgr=self.notes_mgr,
            subject_mgr=self.subject_mgr
        )

        self.views["notifications"] = NotificationsView(
            self.viewport,
            notif_mgr=self.notif_mgr,
            task_mgr=self.task_mgr,
            on_navigate=self.show_view
        )

        # Place all views in the same grid cell
        for view in self.views.values():
            view.grid(row=0, column=0, sticky="nsew")

    def show_view(self, route_name: str) -> None:
        """
        Switches the active view in the viewport and refreshes its dynamic data.
        """
        target_view = self.views.get(route_name)
        if not target_view:
            return

        # Bring chosen view to top of the stack
        target_view.tkraise()

        # Update sidebar highlight
        self.sidebar.set_active_route(route_name)

        # Refresh view data
        if hasattr(target_view, "refresh"):
            target_view.refresh()

        # Update notification badges across UI
        self._refresh_notification_badges()

    def _refresh_notification_badges(self) -> None:
        """Updates badge indicators on Topbar and Sidebar."""
        counts = self.notif_mgr.get_notification_counts()
        badge_count = counts["badge_count"]

        self.sidebar.update_notification_badge(badge_count)
        self.topbar.set_badge_indicator(has_alerts=(badge_count > 0))

    def _open_quick_task(self) -> None:
        """Quick shortcut modal to add a new task from the topbar."""
        TaskDialog(
            self,
            self.task_mgr,
            self.subject_mgr,
            on_save_callback=self._on_task_saved
        )

    def _on_task_saved(self) -> None:
        """Refreshes active view and badges when a task is saved."""
        active_route = self.sidebar.active_route
        active_view = self.views.get(active_route)
        if active_view and hasattr(active_view, "refresh"):
            active_view.refresh()
        self._refresh_notification_badges()

    # --------------------------------------------------------------------------
    # Demo & Reset Handlers
    # --------------------------------------------------------------------------
    def _handle_load_demo_data(self) -> None:
        """
        Seeds realistic Computer Science student records into SQLite.
        """
        if messagebox.askyesno(
            "Load Demo Dataset",
            "This will seed realistic academic data (B.Tech CSE courses, lab tasks, focus sessions, notes, and quiz history).\n\nExisting records will be refreshed. Proceed?"
        ):
            self.db.load_demo_data()
            self._refresh_all_views()
            messagebox.showinfo("Success 🎉", "Demo dataset loaded successfully!\nInspect the Dashboard and Analytics to see your populated charts and metrics.")

    def _handle_clear_data(self) -> None:
        """
        Clears all records for a fresh slate.
        """
        if messagebox.askyesno(
            "Reset Database",
            "Are you sure you want to delete all tasks, subjects, notes, and study sessions? This cannot be undone."
        ):
            self.db.clear_all_data()
            self._refresh_all_views()
            messagebox.showinfo("Reset Complete", "All database tables have been cleared.")

    def _refresh_all_views(self) -> None:
        """Refreshes all instantiated views and badges."""
        for v in self.views.values():
            if hasattr(v, "refresh"):
                v.refresh()
        self._refresh_notification_badges()


def main():
    """Application launcher."""
    app = StudySphereApp()
    app.mainloop()


if __name__ == "__main__":
    main()
