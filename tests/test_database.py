"""
Unit tests for StudySphere Database Manager.
Verifies table creation, CRUD operations, foreign key constraints,
and demo data loading in an isolated temporary/test database.
"""

import unittest
import os
import tempfile
from pathlib import Path
from database.db_manager import DatabaseManager


class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        """Create a temporary database file for isolated testing."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_studysphere.db"
        self.db = DatabaseManager(db_path=str(self.db_path))

    def tearDown(self):
        """Clean up the temporary directory."""
        self.temp_dir.cleanup()

    def test_tables_created(self):
        """Check that all required tables exist in the schema."""
        tables = self.db.fetch_all(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        )
        table_names = {t["name"] for t in tables}
        expected = {"subjects", "tasks", "study_sessions", "notes", "quiz_attempts"}
        self.assertTrue(expected.issubset(table_names), f"Missing tables: {expected - table_names}")

    def test_subject_crud(self):
        """Test inserting, reading, updating, and deleting a subject."""
        # Insert
        sub_id = self.db.execute_insert(
            "INSERT INTO subjects (name, code, color, description) VALUES (?, ?, ?, ?)",
            ("Data Mining", "DS301", "#3B82F6", "Data mining techniques")
        )
        self.assertGreater(sub_id, 0)

        # Read
        sub = self.db.fetch_one("SELECT * FROM subjects WHERE id = ?", (sub_id,))
        self.assertIsNotNone(sub)
        self.assertEqual(sub["name"], "Data Mining")
        self.assertEqual(sub["code"], "DS301")

        # Update
        updated = self.db.execute_query(
            "UPDATE subjects SET description = ? WHERE id = ?",
            ("Advanced Data Mining & Warehouse", sub_id)
        )
        self.assertEqual(updated, 1)
        sub_updated = self.db.fetch_one("SELECT * FROM subjects WHERE id = ?", (sub_id,))
        self.assertEqual(sub_updated["description"], "Advanced Data Mining & Warehouse")

        # Delete
        deleted = self.db.execute_query("DELETE FROM subjects WHERE id = ?", (sub_id,))
        self.assertEqual(deleted, 1)
        self.assertIsNone(self.db.fetch_one("SELECT * FROM subjects WHERE id = ?", (sub_id,)))

    def test_task_crud_and_foreign_key(self):
        """Test task creation with subject relationship and foreign key cascade/set null."""
        # Insert subject
        sub_id = self.db.execute_insert(
            "INSERT INTO subjects (name, code) VALUES (?, ?)",
            ("Operating Systems", "CS203")
        )

        # Insert task
        task_id = self.db.execute_insert(
            """
            INSERT INTO tasks (subject_id, title, description, priority, due_date, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (sub_id, "Thread Synchronization Lab", "Use mutexes & semaphores", "High", "2026-12-01", "Pending")
        )
        self.assertGreater(task_id, 0)

        task = self.db.fetch_one("SELECT * FROM tasks WHERE id = ?", (task_id,))
        self.assertEqual(task["title"], "Thread Synchronization Lab")
        self.assertEqual(task["subject_id"], sub_id)
        self.assertEqual(task["status"], "Pending")

        # Delete subject -> subject_id in tasks should become NULL (ON DELETE SET NULL)
        self.db.execute_query("DELETE FROM subjects WHERE id = ?", (sub_id,))
        task_after = self.db.fetch_one("SELECT * FROM tasks WHERE id = ?", (task_id,))
        self.assertIsNone(task_after["subject_id"])

    def test_demo_data_loader(self):
        """Test that load_demo_data seeds real, valid records in all tables."""
        self.db.load_demo_data()

        subjects = self.db.fetch_all("SELECT * FROM subjects")
        tasks = self.db.fetch_all("SELECT * FROM tasks")
        sessions = self.db.fetch_all("SELECT * FROM study_sessions")
        notes = self.db.fetch_all("SELECT * FROM notes")
        quizzes = self.db.fetch_all("SELECT * FROM quiz_attempts")

        self.assertGreaterEqual(len(subjects), 4)
        self.assertGreaterEqual(len(tasks), 5)
        self.assertGreaterEqual(len(sessions), 5)
        self.assertGreaterEqual(len(notes), 2)
        self.assertGreaterEqual(len(quizzes), 2)


if __name__ == "__main__":
    unittest.main()
