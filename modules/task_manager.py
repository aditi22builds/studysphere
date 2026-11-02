"""
==============================================================================
StudySphere — Task Manager Module
==============================================================================
Author: Senior Python Mentor & Architect
Role: Manages full CRUD operations, filtering, searching, overdue tracking,
      and regex validation for academic tasks.

Python Concepts Used:
- Object-Oriented Architecture (TaskManager domain service)
- Regular Expressions (`re` module) for robust date validation (YYYY-MM-DD)
- Datetime arithmetic for deadline calculations and overdue status
- SQL JOIN queries to aggregate subject names and color badges with tasks
"""

import re
from datetime import datetime, date
from database.db_manager import DatabaseManager


class TaskManager:
    """
    Handles all business logic for academic tasks:
    CRUD, multi-criteria filtering, search, sorting, and deadline notifications.
    """

    DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    def __init__(self, db_manager: DatabaseManager):
        """
        Initializes the TaskManager with a DatabaseManager instance.
        Demonstrates Dependency Injection.
        """
        self.db = db_manager

    def validate_task_input(self, title: str, due_date: str, priority: str) -> None:
        """
        Validates input parameters before saving to SQLite.
        Raises ValueError with a user-friendly message if validation fails.
        """
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty.")

        if len(title.strip()) > 120:
            raise ValueError("Task title exceeds maximum length of 120 characters.")

        if not due_date or not self.DATE_REGEX.match(due_date.strip()):
            raise ValueError("Invalid due date format. Please use YYYY-MM-DD (e.g., 2026-11-15).")

        # Validate that the date is a real calendar date
        try:
            datetime.strptime(due_date.strip(), "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid calendar date. Please enter a valid day/month combination.")

        if priority not in ("Low", "Medium", "High"):
            raise ValueError("Priority must be one of: 'Low', 'Medium', 'High'.")

    def add_task(self, title: str, subject_id: int | None, priority: str,
                 due_date: str, description: str = "", status: str = "Pending") -> int:
        """
        Creates a new task in the database after validating inputs.
        """
        self.validate_task_input(title, due_date, priority)

        sql = """
            INSERT INTO tasks (subject_id, title, description, priority, due_date, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        task_id = self.db.execute_insert(
            sql,
            (subject_id if subject_id else None, title.strip(), description.strip(), priority, due_date.strip(), status)
        )
        return task_id

    def update_task(self, task_id: int, title: str, subject_id: int | None,
                    priority: str, due_date: str, description: str, status: str) -> bool:
        """
        Updates an existing task. Sets completed_at timestamp if status changed to 'Completed'.
        """
        self.validate_task_input(title, due_date, priority)

        completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if status == "Completed" else None

        sql = """
            UPDATE tasks
            SET subject_id = ?, title = ?, description = ?, priority = ?,
                due_date = ?, status = ?, completed_at = ?
            WHERE id = ?
        """
        rows = self.db.execute_query(
            sql,
            (subject_id if subject_id else None, title.strip(), description.strip(),
             priority, due_date.strip(), status, completed_at, task_id)
        )
        return rows > 0

    def toggle_task_status(self, task_id: int) -> str:
        """
        Convenience method to flip status between Pending/In Progress and Completed.
        Returns the new status string.
        """
        task = self.get_task_by_id(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found.")

        if task["status"] == "Completed":
            new_status = "Pending"
            completed_at = None
        else:
            new_status = "Completed"
            completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.db.execute_query(
            "UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?",
            (new_status, completed_at, task_id)
        )
        return new_status

    def delete_task(self, task_id: int) -> bool:
        """
        Deletes a task by ID.
        """
        rows = self.db.execute_query("DELETE FROM tasks WHERE id = ?", (task_id,))
        return rows > 0

    def get_task_by_id(self, task_id: int) -> dict | None:
        """
        Retrieves a single task joined with subject information.
        """
        sql = """
            SELECT t.*, s.name AS subject_name, s.code AS subject_code, s.color AS subject_color
            FROM tasks t
            LEFT JOIN subjects s ON t.subject_id = s.id
            WHERE t.id = ?
        """
        task = self.db.fetch_one(sql, (task_id,))
        if task:
            task["is_overdue"] = self._check_is_overdue(task["due_date"], task["status"])
        return task

    def get_tasks(self, status: str = None, priority: str = None,
                  subject_id: int = None, search_query: str = None,
                  sort_by: str = "due_date") -> list[dict]:
        """
        Fetches tasks with dynamic multi-criteria filtering and searching.
        
        Args:
            status: Filter by 'Pending', 'In Progress', 'Completed', or None for all.
            priority: Filter by 'Low', 'Medium', 'High', or None for all.
            subject_id: Filter by specific subject ID.
            search_query: Search text matching title or description.
            sort_by: Ordering - 'due_date', 'priority', 'created_at'.
        """
        sql = """
            SELECT t.*, s.name AS subject_name, s.code AS subject_code, s.color AS subject_color
            FROM tasks t
            LEFT JOIN subjects s ON t.subject_id = s.id
            WHERE 1=1
        """
        params = []

        if status and status != "All":
            sql += " AND t.status = ?"
            params.append(status)

        if priority and priority != "All":
            sql += " AND t.priority = ?"
            params.append(priority)

        if subject_id and subject_id != "All":
            sql += " AND t.subject_id = ?"
            params.append(int(subject_id))

        if search_query and search_query.strip():
            # Use LIKE with wildcards for text search
            sql += " AND (t.title LIKE ? OR t.description LIKE ?)"
            term = f"%{search_query.strip()}%"
            params.extend([term, term])

        # Ordering
        if sort_by == "priority":
            # High -> Medium -> Low
            sql += " ORDER BY CASE t.priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END, t.due_date ASC"
        elif sort_by == "created_at":
            sql += " ORDER BY t.created_at DESC"
        else:
            # Default: earliest due date first
            sql += " ORDER BY t.due_date ASC, t.id DESC"

        tasks = self.db.fetch_all(sql, tuple(params))
        
        # Enrich each task with overdue calculations
        for task in tasks:
            task["is_overdue"] = self._check_is_overdue(task["due_date"], task["status"])
            task["days_remaining"] = self._calculate_days_remaining(task["due_date"])

        return tasks

    def get_upcoming_deadlines(self, limit: int = 5) -> list[dict]:
        """
        Returns imminent tasks that are not yet completed, ordered by due date.
        """
        today_str = date.today().isoformat()
        sql = """
            SELECT t.*, s.name AS subject_name, s.code AS subject_code, s.color AS subject_color
            FROM tasks t
            LEFT JOIN subjects s ON t.subject_id = s.id
            WHERE t.status != 'Completed' AND t.due_date >= ?
            ORDER BY t.due_date ASC
            LIMIT ?
        """
        tasks = self.db.fetch_all(sql, (today_str, limit))
        for t in tasks:
            t["days_remaining"] = self._calculate_days_remaining(t["due_date"])
        return tasks

    def get_overdue_tasks(self) -> list[dict]:
        """
        Returns all uncompleted tasks whose due date is prior to today.
        """
        today_str = date.today().isoformat()
        sql = """
            SELECT t.*, s.name AS subject_name, s.code AS subject_code, s.color AS subject_color
            FROM tasks t
            LEFT JOIN subjects s ON t.subject_id = s.id
            WHERE t.status != 'Completed' AND t.due_date < ?
            ORDER BY t.due_date ASC
        """
        tasks = self.db.fetch_all(sql, (today_str,))
        for t in tasks:
            t["days_overdue"] = abs(self._calculate_days_remaining(t["due_date"]))
        return tasks

    def get_task_counts(self) -> dict:
        """
        Returns a dictionary of task statistics calculated directly from the database.
        """
        all_tasks = self.db.fetch_all("SELECT status, due_date FROM tasks")
        today_str = date.today().isoformat()

        total = len(all_tasks)
        completed = sum(1 for t in all_tasks if t["status"] == "Completed")
        pending = sum(1 for t in all_tasks if t["status"] == "Pending")
        in_progress = sum(1 for t in all_tasks if t["status"] == "In Progress")
        overdue = sum(1 for t in all_tasks if t["status"] != "Completed" and t["due_date"] < today_str)

        completion_rate = (completed / total * 100) if total > 0 else 0.0

        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "in_progress": in_progress,
            "overdue": overdue,
            "completion_rate": round(completion_rate, 1)
        }

    # --------------------------------------------------------------------------
    # Helper Date Logic
    # --------------------------------------------------------------------------
    def _check_is_overdue(self, due_date_str: str, status: str) -> bool:
        """Determines if a task is overdue."""
        if status == "Completed":
            return False
        try:
            task_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            return task_date < date.today()
        except ValueError:
            return False

    def _calculate_days_remaining(self, due_date_str: str) -> int:
        """Calculates difference in days between due date and today."""
        try:
            task_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            return (task_date - date.today()).days
        except ValueError:
            return 0
