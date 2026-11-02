"""
Unit tests for StudySphere Business Logic Modules.
Validates TaskManager, SubjectManager, FocusTimer, AnalyticsEngine,
QuizManager, NotesManager, and NotificationManager.
"""

import unittest
import tempfile
from pathlib import Path
from datetime import date, timedelta

from database.db_manager import DatabaseManager
from modules.task_manager import TaskManager
from modules.subject_manager import SubjectManager
from modules.focus_timer import FocusTimer
from modules.analytics import AnalyticsEngine
from modules.quiz import QuizManager
from modules.notes import NotesManager
from modules.notifications import NotificationManager


class TestStudySphereModules(unittest.TestCase):
    def setUp(self):
        """Set up an isolated temporary database for each test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_modules.db"
        self.db = DatabaseManager(db_path=str(self.db_path))

        # Instantiate all services
        self.subjects = SubjectManager(self.db)
        self.tasks = TaskManager(self.db)
        self.timer = FocusTimer(self.db)
        self.analytics = AnalyticsEngine(self.db)
        self.quiz = QuizManager(self.db)
        self.notes = NotesManager(self.db)
        self.notifs = NotificationManager(self.db)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_task_manager_validation_and_crud(self):
        # Validation checks
        with self.assertRaises(ValueError):
            self.tasks.add_task("", None, "Medium", "2026-12-01")  # empty title

        with self.assertRaises(ValueError):
            self.tasks.add_task("Test", None, "InvalidPriority", "2026-12-01")  # bad priority

        with self.assertRaises(ValueError):
            self.tasks.add_task("Test", None, "High", "invalid-date")  # bad date regex

        # Add valid subject and task
        sub_id = self.subjects.add_subject("Algorithms", "CS201", "#8B5CF6")
        task_id = self.tasks.add_task("Binary Search Tree", sub_id, "High", "2026-12-10", "Implement deletion")
        self.assertGreater(task_id, 0)

        # Toggle status
        new_status = self.tasks.toggle_task_status(task_id)
        self.assertEqual(new_status, "Completed")
        task = self.tasks.get_task_by_id(task_id)
        self.assertEqual(task["status"], "Completed")
        self.assertIsNotNone(task["completed_at"])

        # Toggle back
        new_status = self.tasks.toggle_task_status(task_id)
        self.assertEqual(new_status, "Pending")

    def test_subject_manager_metrics(self):
        sub_id = self.subjects.add_subject("Discrete Maths", "MA101", "#F59E0B")
        self.tasks.add_task("Proof Set A", sub_id, "Medium", "2026-12-05")
        self.tasks.add_task("Proof Set B", sub_id, "Low", "2026-12-06")

        sub_list = self.subjects.get_subjects_with_task_counts()
        self.assertEqual(len(sub_list), 1)
        self.assertEqual(sub_list[0]["total_tasks"], 2)
        self.assertEqual(sub_list[0]["pending_tasks"], 2)

    def test_focus_timer_tick_and_save(self):
        sub_id = self.subjects.add_subject("Python", "PY101")
        self.timer.active_subject_id = sub_id
        self.timer.total_seconds = 2
        self.timer.remaining_seconds = 2
        self.timer.start()

        # Tick 1
        completed = self.timer.tick()
        self.assertFalse(completed)
        self.assertEqual(self.timer.remaining_seconds, 1)

        # Tick 2 -> should complete and save
        completed = self.timer.tick()
        self.assertTrue(completed)
        self.assertEqual(self.timer.state, FocusTimer.STATE_COMPLETED)

        recent = self.timer.get_recent_sessions(limit=5)
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0]["subject_id"], sub_id)

    def test_analytics_with_numpy(self):
        self.db.load_demo_data()
        stats = self.analytics.get_summary_statistics()

        self.assertIn("total_hours", stats)
        self.assertGreater(stats["total_hours"], 0)
        self.assertIn("mean_session_min", stats)
        self.assertIn("consistency_score", stats)

        daily = self.analytics.get_daily_study_hours(days=7)
        self.assertEqual(len(daily), 7)

        dist = self.analytics.get_subject_distribution()
        self.assertGreaterEqual(len(dist), 1)

    def test_quiz_manager(self):
        questions = self.quiz.start_quiz(difficulty="All", num_questions=3)
        self.assertEqual(len(questions), 3)

        # Answer all questions
        for idx in range(3):
            self.quiz.record_answer(questions[idx]["answer_index"])
            if idx < 2:
                self.quiz.next_question()

        results = self.quiz.finish_quiz()
        self.assertEqual(results["score"], 3)
        self.assertEqual(results["percentage"], 100.0)

        history = self.quiz.get_past_attempts()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["score"], 3)

    def test_notes_manager(self):
        sub_id = self.subjects.add_subject("Operating Systems", "CS203")
        note_id = self.notes.add_note("Process Scheduling", "FCFS, SJF, Round Robin", sub_id, "scheduling,cpu")
        self.assertGreater(note_id, 0)

        # Search
        results = self.notes.get_notes(search_query="Round Robin")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Process Scheduling")

        # Update
        self.notes.update_note(note_id, "CPU Process Scheduling", "Updated content", sub_id, "scheduling")
        updated_note = self.notes.get_note_by_id(note_id)
        self.assertEqual(updated_note["title"], "CPU Process Scheduling")

    def test_notifications_manager(self):
        today = date.today()
        # Add overdue task
        self.tasks.add_task("Overdue Lab", None, "High", (today - timedelta(days=2)).isoformat())
        # Add task due today
        self.tasks.add_task("Due Today Task", None, "Medium", today.isoformat())

        notifs = self.notifs.get_all_notifications()
        severities = [n["severity"] for n in notifs]
        self.assertIn(NotificationManager.SEV_CRITICAL, severities)
        self.assertIn(NotificationManager.SEV_WARNING, severities)


if __name__ == "__main__":
    unittest.main()
