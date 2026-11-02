"""
==============================================================================
StudySphere — Subject Manager Module
==============================================================================
Author: Senior Python Mentor & Architect
Role: Manages academic courses/subjects, their visual tags, and aggregates
      task and focus-session metrics per subject.

Python Concepts Used:
- Object-Oriented Programming (SubjectManager service class)
- Advanced SQL Aggregations (GROUP BY, COUNT, SUM, COALESCE)
- Input sanitization and hex color format validation
"""

import re
from database.db_manager import DatabaseManager


class SubjectManager:
    """
    Handles business logic for academic subjects:
    CRUD operations, color badges, and course-level task aggregations.
    """

    HEX_COLOR_REGEX = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")

    DEFAULT_COLORS = [
        "#8B5CF6",  # Purple
        "#3B82F6",  # Blue
        "#10B981",  # Emerald
        "#EC4899",  # Pink
        "#F59E0B",  # Amber
        "#6366F1",  # Indigo
        "#06B6D4",  # Cyan
        "#EF4444",  # Rose
    ]

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def validate_subject_input(self, name: str, code: str, color: str = None) -> None:
        """
        Validates subject properties.
        """
        if not name or not name.strip():
            raise ValueError("Subject name cannot be empty.")

        if len(name.strip()) > 80:
            raise ValueError("Subject name cannot exceed 80 characters.")

        if not code or not code.strip():
            raise ValueError("Course code cannot be empty (e.g. CS201).")

        if len(code.strip()) > 15:
            raise ValueError("Course code cannot exceed 15 characters.")

        if color and not self.HEX_COLOR_REGEX.match(color.strip()):
            raise ValueError("Subject color must be a valid hex color code (e.g. #8B5CF6).")

    def add_subject(self, name: str, code: str, color: str = "#8B5CF6", description: str = "") -> int:
        """
        Adds a new academic subject. Checks for uniqueness.
        """
        self.validate_subject_input(name, code, color)

        # Check for duplicate name
        existing = self.db.fetch_one("SELECT id FROM subjects WHERE LOWER(name) = LOWER(?)", (name.strip(),))
        if existing:
            raise ValueError(f"A subject with the name '{name.strip()}' already exists.")

        sql = """
            INSERT INTO subjects (name, code, color, description)
            VALUES (?, ?, ?, ?)
        """
        return self.db.execute_insert(sql, (name.strip(), code.strip().upper(), color.strip(), description.strip()))

    def update_subject(self, subject_id: int, name: str, code: str, color: str, description: str) -> bool:
        """
        Updates an existing subject.
        """
        self.validate_subject_input(name, code, color)

        # Check if name is taken by a different subject
        existing = self.db.fetch_one(
            "SELECT id FROM subjects WHERE LOWER(name) = LOWER(?) AND id != ?",
            (name.strip(), subject_id)
        )
        if existing:
            raise ValueError(f"Another subject with the name '{name.strip()}' already exists.")

        sql = """
            UPDATE subjects
            SET name = ?, code = ?, color = ?, description = ?
            WHERE id = ?
        """
        rows = self.db.execute_query(sql, (name.strip(), code.strip().upper(), color.strip(), description.strip(), subject_id))
        return rows > 0

    def delete_subject(self, subject_id: int) -> bool:
        """
        Deletes a subject. Foreign keys in tasks/notes/sessions will set subject_id to NULL.
        """
        rows = self.db.execute_query("DELETE FROM subjects WHERE id = ?", (subject_id,))
        return rows > 0

    def get_subject_by_id(self, subject_id: int) -> dict | None:
        """
        Returns a single subject by ID.
        """
        return self.db.fetch_one("SELECT * FROM subjects WHERE id = ?", (subject_id,))

    def get_all_subjects(self) -> list[dict]:
        """
        Retrieves all subjects ordered alphabetically.
        """
        return self.db.fetch_all("SELECT * FROM subjects ORDER BY name ASC")

    def get_subjects_with_task_counts(self) -> list[dict]:
        """
        Retrieves subjects enriched with metrics:
        - Total tasks
        - Completed tasks
        - Pending tasks
        - Total study hours
        """
        sql = """
            SELECT 
                s.id,
                s.name,
                s.code,
                s.color,
                s.description,
                s.created_at,
                COUNT(DISTINCT t.id) AS total_tasks,
                COUNT(DISTINCT CASE WHEN t.status = 'Completed' THEN t.id END) AS completed_tasks,
                COUNT(DISTINCT CASE WHEN t.status != 'Completed' THEN t.id END) AS pending_tasks,
                ROUND(COALESCE(SUM(ss.duration_minutes), 0) / 60.0, 1) AS study_hours
            FROM subjects s
            LEFT JOIN tasks t ON s.id = t.subject_id
            LEFT JOIN study_sessions ss ON s.id = ss.subject_id AND ss.session_type = 'Focus'
            GROUP BY s.id
            ORDER BY s.name ASC
        """
        subjects = self.db.fetch_all(sql)
        for s in subjects:
            total = s["total_tasks"]
            completed = s["completed_tasks"]
            s["completion_rate"] = round((completed / total * 100), 1) if total > 0 else 0.0
        return subjects

    def get_tasks_for_subject(self, subject_id: int) -> list[dict]:
        """
        Retrieves all tasks associated with a given subject.
        """
        sql = """
            SELECT * FROM tasks
            WHERE subject_id = ?
            ORDER BY due_date ASC
        """
        return self.db.fetch_all(sql, (subject_id,))
