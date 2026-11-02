"""
==============================================================================
StudySphere — Database Manager
==============================================================================
Author: Senior Python Mentor & Architect
Role: Encapsulates all SQLite interactions, connection lifecycle,
      parameterized execution, transaction handling, and schema setup.

Python Concepts Used:
- Object-Oriented Programming (Singleton-style service class, Encapsulation)
- Context Managers (`@contextmanager` and `with` statement for deterministic resource cleanup)
- Parameterized SQL (Protects against SQL Injection vulnerabilities)
- Pathlib for cross-platform OS path handling
"""

import os
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from contextlib import contextmanager
import random


class DatabaseManager:
    """
    Manages SQLite database connections, schema setup, and query execution.
    Ensures safe resource handling and parameterization.
    """

    def __init__(self, db_path: str = None):
        """
        Initializes the DatabaseManager.
        
        Args:
            db_path: Optional custom path to the SQLite file. If None,
                     defaults to 'database/studysphere.db'.
        """
        if db_path is None:
            # Place database in the same directory as this file
            base_dir = Path(__file__).resolve().parent
            self.db_path = base_dir / "studysphere.db"
        else:
            self.db_path = Path(db_path)

        # Ensure the directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize schema upon construction
        self.initialize_database()

    @contextmanager
    def get_connection(self):
        """
        Context manager that opens an SQLite connection, enables foreign keys,
        yields the connection for queries, commits transactions, and guarantees
        the connection is closed upon exit (preventing Windows file-lock errors).
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Allows accessing columns by name: row['title']
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize_database(self) -> None:
        """
        Reads and executes the schema.sql script to build tables and indexes.
        Safe to call multiple times because of 'CREATE TABLE IF NOT EXISTS'.
        """
        schema_path = Path(__file__).resolve().parent / "schema.sql"
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found at: {schema_path}")

        with open(schema_path, "r", encoding="utf-8") as f:
            schema_script = f.read()

        with self.get_connection() as conn:
            conn.executescript(schema_script)

    def execute_query(self, sql: str, params: tuple = ()) -> int:
        """
        Executes an UPDATE, INSERT, or DELETE query.
        
        Returns:
            The number of rows affected.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor.rowcount

    def execute_insert(self, sql: str, params: tuple = ()) -> int:
        """
        Executes an INSERT query and returns the newly generated row ID.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor.lastrowid

    def fetch_all(self, sql: str, params: tuple = ()) -> list[dict]:
        """
        Executes a SELECT query and returns all matching records as a list of dicts.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def fetch_one(self, sql: str, params: tuple = ()) -> dict | None:
        """
        Executes a SELECT query and returns the first matching record or None.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            row = cursor.fetchone()
            return dict(row) if row else None

    # --------------------------------------------------------------------------
    # DEMO DATA LOADER (Explicitly triggered by user/tester)
    # --------------------------------------------------------------------------
    def load_demo_data(self) -> None:
        """
        Seeds the database with realistic, high-quality sample data
        representative of a 2nd-Year B.Tech Computer Science & Data Science student.
        """
        # Clear existing data first to avoid duplicate unique violations
        self.clear_all_data()

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Seed Subjects
            subjects = [
                ("Python & Advanced Data Structures", "CS201", "#8B5CF6", "Advanced Python programming, graph algorithms, trees, and time complexity."),
                ("Machine Learning & NumPy", "DS204", "#EC4899", "Statistical learning, vectorization, gradient descent, and regression models."),
                ("Database Management Systems", "CS202", "#10B981", "Relational algebra, SQL optimization, ACID transactions, and 3NF normalization."),
                ("Discrete Mathematics", "MA201", "#F59E0B", "Graph theory, combinatorics, proof by induction, and predicate logic."),
                ("Computer Networks", "CS205", "#3B82F6", "TCP/IP protocol stack, socket programming, routing algorithms, and DNS architecture.")
            ]
            subject_ids = {}
            for name, code, color, desc in subjects:
                cursor.execute(
                    "INSERT INTO subjects (name, code, color, description) VALUES (?, ?, ?, ?)",
                    (name, code, color, desc)
                )
                subject_ids[code] = cursor.lastrowid

            today = datetime.now()
            
            # 2. Seed Tasks (variety of priorities, statuses, and due dates)
            tasks = [
                (subject_ids["CS201"], "Implement Red-Black Tree Balancing in Python", "Write complete rotate_left, rotate_right methods with test cases.", "High", (today + timedelta(days=2)).strftime("%Y-%m-%d"), "In Progress", None),
                (subject_ids["DS204"], "Vectorized Gradient Descent with NumPy", "Avoid all for-loops in cost function calculation and plot learning curve.", "High", (today + timedelta(days=1)).strftime("%Y-%m-%d"), "Pending", None),
                (subject_ids["CS202"], "Complete DBMS Normalization Lab Report", "Decompose student enrollment tables to 3NF and BCNF with functional dependencies.", "Medium", (today + timedelta(days=5)).strftime("%Y-%m-%d"), "Pending", None),
                (subject_ids["MA201"], "Solve Discrete Maths Induction Problems", "Exercises 4.1 to 4.15 on strong induction and recurrence relations.", "Low", (today - timedelta(days=1)).strftime("%Y-%m-%d"), "Completed", (today - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")),
                (subject_ids["CS205"], "Socket Programming Client-Server Echo in Python", "Implement multi-threaded TCP server handling concurrent connections.", "Medium", (today + timedelta(days=4)).strftime("%Y-%m-%d"), "In Progress", None),
                (subject_ids["DS204"], "Exploratory Data Analysis on Housing Dataset", "Compute mean, median, IQR, outliers and correlation matrix using NumPy.", "Medium", (today - timedelta(days=3)).strftime("%Y-%m-%d"), "Completed", (today - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")),
                (subject_ids["CS201"], "LeetCode Medium: 3 Graph Traversal Problems", "Practice BFS/DFS on grid islands and shortest path unweighted graphs.", "High", (today - timedelta(days=2)).strftime("%Y-%m-%d"), "Completed", (today - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")),
                (subject_ids["MA201"], "Prepare for Unit Test 2 - Combinatorics", "Review permutations, combinations, and pigeonhole principle proofs.", "High", (today - timedelta(days=1)).strftime("%Y-%m-%d"), "Pending", None), # Overdue task for alert testing
            ]
            for sub_id, title, desc, prio, due, status, comp in tasks:
                cursor.execute(
                    """
                    INSERT INTO tasks (subject_id, title, description, priority, due_date, status, completed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (sub_id, title, desc, prio, due, status, comp)
                )

            # 3. Seed Study Sessions over the last 7 days
            sessions = [
                (subject_ids["CS201"], 50.0, "Focus", "Deep work on binary tree traversal & recursion", (today - timedelta(days=6, hours=3)).strftime("%Y-%m-%d %H:%M:%S")),
                (subject_ids["CS201"], 10.0, "Short Break", "Coffee and stretch", (today - timedelta(days=6, hours=2)).strftime("%Y-%m-%d %H:%M:%S")),
                (subject_ids["DS204"], 60.0, "Focus", "NumPy matrix broadcasting and linear regression", (today - timedelta(days=5, hours=4)).strftime("%Y-%m-%d %H:%M:%S")),
                (subject_ids["CS202"], 45.0, "Focus", "SQL joins, indexing strategies, and EXPLAIN plans", (today - timedelta(days=4, hours=5)).strftime("%Y-%m-%d %H:%M:%S")),
                (subject_ids["CS205"], 50.0, "Focus", "Wireshark packet capture analysis & TCP handshakes", (today - timedelta(days=3, hours=2)).strftime("%Y-%m-%d %H:%M:%S")),
                (subject_ids["DS204"], 75.0, "Focus", "Model evaluation metrics: Precision, Recall, F1", (today - timedelta(days=2, hours=6)).strftime("%Y-%m-%d %H:%M:%S")),
                (subject_ids["CS201"], 60.0, "Focus", "Graph Dijkstra shortest path algorithm in Python", (today - timedelta(days=1, hours=3)).strftime("%Y-%m-%d %H:%M:%S")),
                (subject_ids["DS204"], 50.0, "Focus", "Hyperparameter tuning and cross validation", today.strftime("%Y-%m-%d %H:%M:%S")),
            ]
            for sub_id, dur, stype, notes, comp in sessions:
                cursor.execute(
                    """
                    INSERT INTO study_sessions (subject_id, duration_minutes, session_type, notes, completed_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (sub_id, dur, stype, notes, comp)
                )

            # 4. Seed Academic Notes
            notes_data = [
                (subject_ids["CS201"], "Python Dunder Methods & Operator Overloading",
                 "# Special Methods in Python\n\n- `__init__`: Constructor\n- `__repr__` vs `__str__`: Unambiguous vs human-readable string\n- `__len__`, `__getitem__`: Makes custom objects behave like sequences\n- `__eq__`, `__lt__`: Enables rich comparisons\n\n```python\nclass Student:\n    def __init__(self, name, gpa):\n        self.name = name\n        self.gpa = gpa\n    def __repr__(self):\n        return f'Student({self.name!r}, {self.gpa})'\n```",
                 "python,oop,dunder"),
                (subject_ids["DS204"], "NumPy Vectorization vs Native Python Loops",
                 "# Why Vectorization Matters\n\nNumPy arrays are stored in contiguous memory blocks with homogeneous types. Operating on them triggers compiled C/Fortran SIMD loops rather than Python interpreter overhead.\n\n- **Dot product**: `np.dot(A, B)` is up to 50x faster than list comprehensions.\n- **Broadcasting rule**: Dimensions must either match or one of them must be 1.",
                 "numpy,datascience,performance"),
                (subject_ids["CS202"], "Database Indexing & B+ Trees Summary",
                 "# B+ Tree Indexes\n\n- Clustered Index: Determines physical order of data on disk (Primary Key).\n- Non-Clustered Index: Separate structure containing pointers to heap/clustered index.\n- Composite Index: Order of columns matters (Left-to-right prefix matching).",
                 "dbms,sql,indexing"),
            ]
            for sub_id, title, content, tags in notes_data:
                cursor.execute(
                    """
                    INSERT INTO notes (subject_id, title, content, tags)
                    VALUES (?, ?, ?, ?)
                    """,
                    (sub_id, title, content, tags)
                )

            # 5. Seed Quiz Attempts
            quizzes = [
                ("Python Core & Data Structures", "Intermediate", 8, 10, 185, (today - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")),
                ("NumPy & Data Manipulation", "Beginner", 9, 10, 140, (today - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")),
                ("Object-Oriented Programming in Python", "Advanced", 7, 10, 210, (today - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")),
            ]
            for topic, diff, score, total, time_spent, comp in quizzes:
                cursor.execute(
                    """
                    INSERT INTO quiz_attempts (topic, difficulty, score, total_questions, time_spent_seconds, completed_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (topic, diff, score, total, time_spent, comp)
                )

    def clear_all_data(self) -> None:
        """
        Removes all records from all tables while maintaining the schema.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM quiz_attempts;")
            cursor.execute("DELETE FROM notes;")
            cursor.execute("DELETE FROM study_sessions;")
            cursor.execute("DELETE FROM tasks;")
            cursor.execute("DELETE FROM subjects;")
