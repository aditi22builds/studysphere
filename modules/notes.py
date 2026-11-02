"""
==============================================================================
StudySphere — Notes Manager Module
==============================================================================
Author: Senior Python Mentor & Architect
Role: Manages persistent academic lecture notes, formula sheets, code snippets,
      subject tagging, and real-time full-text search.

Python Concepts Used:
- Object-Oriented Architecture (NotesManager service)
- SQL LIKE pattern matching for search queries
- Datetime timestamp auditing (created_at, updated_at)
"""

from datetime import datetime
from database.db_manager import DatabaseManager


class NotesManager:
    """
    Handles business logic for student notes:
    CRUD, subject association, tag categorization, and multi-field search.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def validate_note_input(self, title: str, content: str) -> None:
        """Validates note title and body content."""
        if not title or not title.strip():
            raise ValueError("Note title cannot be empty.")
        if len(title.strip()) > 150:
            raise ValueError("Note title cannot exceed 150 characters.")
        if not content or not content.strip():
            raise ValueError("Note content cannot be empty.")

    def add_note(self, title: str, content: str, subject_id: int | None = None, tags: str = "") -> int:
        """
        Creates a new note.
        """
        self.validate_note_input(title, content)

        sql = """
            INSERT INTO notes (subject_id, title, content, tags)
            VALUES (?, ?, ?, ?)
        """
        return self.db.execute_insert(
            sql,
            (subject_id if subject_id else None, title.strip(), content.strip(), tags.strip())
        )

    def update_note(self, note_id: int, title: str, content: str,
                    subject_id: int | None = None, tags: str = "") -> bool:
        """
        Updates an existing note and refreshes updated_at timestamp.
        """
        self.validate_note_input(title, content)

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = """
            UPDATE notes
            SET subject_id = ?, title = ?, content = ?, tags = ?, updated_at = ?
            WHERE id = ?
        """
        rows = self.db.execute_query(
            sql,
            (subject_id if subject_id else None, title.strip(), content.strip(), tags.strip(), now_str, note_id)
        )
        return rows > 0

    def delete_note(self, note_id: int) -> bool:
        """Deletes a note by ID."""
        rows = self.db.execute_query("DELETE FROM notes WHERE id = ?", (note_id,))
        return rows > 0

    def get_note_by_id(self, note_id: int) -> dict | None:
        """Retrieves a single note joined with subject details."""
        sql = """
            SELECT n.*, s.name AS subject_name, s.code AS subject_code, s.color AS subject_color
            FROM notes n
            LEFT JOIN subjects s ON n.subject_id = s.id
            WHERE n.id = ?
        """
        return self.db.fetch_one(sql, (note_id,))

    def get_notes(self, subject_id: int = None, search_query: str = None) -> list[dict]:
        """
        Retrieves notes with optional subject filtering and keyword search.
        """
        sql = """
            SELECT n.*, s.name AS subject_name, s.code AS subject_code, s.color AS subject_color
            FROM notes n
            LEFT JOIN subjects s ON n.subject_id = s.id
            WHERE 1=1
        """
        params = []

        if subject_id and subject_id != "All":
            sql += " AND n.subject_id = ?"
            params.append(int(subject_id))

        if search_query and search_query.strip():
            sql += " AND (n.title LIKE ? OR n.content LIKE ? OR n.tags LIKE ?)"
            term = f"%{search_query.strip()}%"
            params.extend([term, term, term])

        sql += " ORDER BY n.updated_at DESC"
        return self.db.fetch_all(sql, tuple(params))

    def get_recent_notes(self, limit: int = 5) -> list[dict]:
        """Fetches recently modified notes."""
        sql = """
            SELECT n.*, s.name AS subject_name, s.code AS subject_code, s.color AS subject_color
            FROM notes n
            LEFT JOIN subjects s ON n.subject_id = s.id
            ORDER BY n.updated_at DESC
            LIMIT ?
        """
        return self.db.fetch_all(sql, (limit,))
