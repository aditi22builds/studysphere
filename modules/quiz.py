"""
==============================================================================
StudySphere — Python Technical Quiz Module
==============================================================================
Author: Senior Python Mentor & Architect
Role: Houses a comprehensive Python & Data Science technical question bank,
      orchestrates randomized quiz rounds, tracks live countdown timing,
      calculates percentage scores, and archives attempt history in SQLite.

Python Concepts Used:
- Randomization (`random.sample`, `random.shuffle`)
- Object-Oriented state management for quiz sessions
- List comprehensions and dictionary mappings
"""

import random
from datetime import datetime
from database.db_manager import DatabaseManager


class QuizManager:
    """
    Manages the question bank, quiz gameplay flow, and score history.
    """

    QUESTION_BANK = [
        # --- Python Basics ---
        {
            "id": 1,
            "topic": "Python Basics",
            "difficulty": "Beginner",
            "question": "What is the output of bool([]) and bool([0]) in Python?",
            "options": [
                "False, True",
                "False, False",
                "True, True",
                "True, False"
            ],
            "answer_index": 0,
            "explanation": "Empty collections like [] evaluate to False (falsy), while a non-empty list like [0] evaluates to True, even if its single element is 0."
        },
        {
            "id": 2,
            "topic": "Python Basics",
            "difficulty": "Beginner",
            "question": "Which operator is used for integer floor division in Python?",
            "options": ["//", "/", "%", "**"],
            "answer_index": 0,
            "explanation": "The // operator performs floor division, rounding down to the nearest integer."
        },
        {
            "id": 3,
            "topic": "Python Basics",
            "difficulty": "Beginner",
            "question": "Which of the following is an immutable data type in Python?",
            "options": ["List", "Dictionary", "Tuple", "Set"],
            "answer_index": 2,
            "explanation": "Tuples are immutable; once created, their elements cannot be modified, added, or removed."
        },
        {
            "id": 4,
            "topic": "Python Basics",
            "difficulty": "Intermediate",
            "question": "What does the *args and **kwargs syntax in a function definition allow?",
            "options": [
                "Arbitrary positional and keyword arguments",
                "Only keyword arguments",
                "Pointers and memory addresses like C++",
                "Required arguments only"
            ],
            "answer_index": 0,
            "explanation": "*args collects variable positional arguments as a tuple, while **kwargs collects variable keyword arguments as a dictionary."
        },

        # --- Data Structures ---
        {
            "id": 5,
            "topic": "Data Structures",
            "difficulty": "Beginner",
            "question": "What is the average time complexity for searching a key in a Python dict?",
            "options": ["O(1)", "O(n)", "O(log n)", "O(n^2)"],
            "answer_index": 0,
            "explanation": "Python dictionaries are implemented using hash tables, giving an average lookup, insertion, and deletion time of O(1)."
        },
        {
            "id": 6,
            "topic": "Data Structures",
            "difficulty": "Intermediate",
            "question": "What is the result of list(set([3, 1, 2, 3, 2, 1]))?",
            "options": [
                "A list containing unique elements [1, 2, 3] (order may vary)",
                "[3, 1, 2, 3, 2, 1]",
                "SyntaxError",
                "A dictionary"
            ],
            "answer_index": 0,
            "explanation": "Passing a list into set() eliminates all duplicate values. Converting it back to a list yields unique elements."
        },
        {
            "id": 7,
            "topic": "Data Structures",
            "difficulty": "Intermediate",
            "question": "What does a list comprehension [x**2 for x in range(5) if x % 2 == 0] produce?",
            "options": ["[0, 4, 16]", "[1, 9]", "[0, 1, 4, 9, 16]", "[4, 16]"],
            "answer_index": 0,
            "explanation": "range(5) produces 0, 1, 2, 3, 4. The filter selects even numbers (0, 2, 4), and squares them to produce [0, 4, 16]."
        },

        # --- OOP in Python ---
        {
            "id": 8,
            "topic": "OOP",
            "difficulty": "Intermediate",
            "question": "Which special dunder method is invoked when str(object) or print(object) is called?",
            "options": ["__str__", "__repr__", "__init__", "__call__"],
            "answer_index": 0,
            "explanation": "__str__ is intended to return a human-readable string representation of the instance."
        },
        {
            "id": 9,
            "topic": "OOP",
            "difficulty": "Intermediate",
            "question": "What does super().__init__() accomplish in a subclass constructor?",
            "options": [
                "Invokes the constructor of the parent/base class",
                "Overwrites parent attributes",
                "Creates a static class instance",
                "Destroys the parent object"
            ],
            "answer_index": 0,
            "explanation": "super() returns a proxy object delegating method calls to a parent or sibling class following the MRO (Method Resolution Order)."
        },
        {
            "id": 10,
            "topic": "OOP",
            "difficulty": "Advanced",
            "question": "What is the purpose of the @property decorator in Python?",
            "options": [
                "Defines getter methods that can be accessed like attributes",
                "Prevents garbage collection of the class",
                "Makes a class method strictly private",
                "Forces asynchronous execution"
            ],
            "answer_index": 0,
            "explanation": "@property allows defining methods that can be accessed syntactically as attributes while encapsulating getter/setter logic."
        },
        {
            "id": 11,
            "topic": "OOP",
            "difficulty": "Advanced",
            "question": "What is the difference between a classmethod and a staticmethod?",
            "options": [
                "classmethod receives 'cls' as first argument; staticmethod receives neither 'self' nor 'cls'",
                "classmethod cannot access class attributes",
                "staticmethod must be called without an instance",
                "They are exact synonyms with identical signatures"
            ],
            "answer_index": 0,
            "explanation": "@classmethod receives the class object 'cls' as its first parameter, allowing factory patterns, whereas @staticmethod is a plain function scoped inside a class."
        },

        # --- NumPy & Data Science ---
        {
            "id": 12,
            "topic": "NumPy & Data Science",
            "difficulty": "Beginner",
            "question": "What is the main advantage of NumPy ndarrays over standard Python lists?",
            "options": [
                "Contiguous memory storage enabling C-speed SIMD vectorization",
                "They can store mixed arbitrary objects without type constraints",
                "They require zero RAM",
                "They automatically save to SQLite"
            ],
            "answer_index": 0,
            "explanation": "NumPy ndarrays are stored in contiguous blocks of memory with uniform data types, allowing vector operations to execute in optimized C/Fortran routines."
        },
        {
            "id": 13,
            "topic": "NumPy & Data Science",
            "difficulty": "Intermediate",
            "question": "If array A has shape (3, 1) and array B has shape (1, 4), what is the shape of A + B via broadcasting?",
            "options": ["(3, 4)", "(3, 1)", "(1, 4)", "ValueError: shapes cannot broadcast"],
            "answer_index": 0,
            "explanation": "NumPy broadcasting compares trailing dimensions. Since both dimensions match or are 1, the result expands to shape (3, 4)."
        },
        {
            "id": 14,
            "topic": "NumPy & Data Science",
            "difficulty": "Intermediate",
            "question": "Which NumPy function computes the arithmetic mean along a specified axis?",
            "options": ["np.mean()", "np.avg()", "np.median()", "np.sum_div()"],
            "answer_index": 0,
            "explanation": "np.mean(a, axis=...) calculates the arithmetic mean of an array along a given axis."
        },
        {
            "id": 15,
            "topic": "NumPy & Data Science",
            "difficulty": "Advanced",
            "question": "What does np.polyfit(x, y, deg=1) compute?",
            "options": [
                "Least-squares polynomial fit coefficients (slope and intercept for deg=1)",
                "Polynomial roots",
                "Fast Fourier Transform",
                "Eigenvalues of matrix x"
            ],
            "answer_index": 0,
            "explanation": "np.polyfit performs a least-squares polynomial fit, returning the slope and intercept coefficients for degree 1 (linear regression)."
        },

        # --- Error Handling & Best Practices ---
        {
            "id": 16,
            "topic": "Python Core",
            "difficulty": "Beginner",
            "question": "Which block in a try-except structure is ALWAYS executed, regardless of whether an exception occurred?",
            "options": ["finally", "else", "except", "catch"],
            "answer_index": 0,
            "explanation": "The 'finally' block is guaranteed to execute, making it ideal for cleaning up resources like closing files or database connections."
        },
        {
            "id": 17,
            "topic": "Python Core",
            "difficulty": "Intermediate",
            "question": "What is a Python generator and which keyword creates one?",
            "options": [
                "A function that returns an iterator using the 'yield' keyword",
                "A class decorator using 'generate'",
                "A multithreaded queue using 'spawn'",
                "A built-in loop construct using 'goto'"
            ],
            "answer_index": 0,
            "explanation": "Generators produce items on demand (lazy evaluation) using the 'yield' keyword, preserving their execution frame across calls."
        },
        {
            "id": 18,
            "topic": "Python Core",
            "difficulty": "Advanced",
            "question": "What is the Global Interpreter Lock (GIL) in standard CPython?",
            "options": [
                "A mutex preventing multiple native threads from executing Python bytecode simultaneously",
                "A security sandbox restricting file system access",
                "A compiler lock that speeds up code execution",
                "A database lock for SQLite transactions"
            ],
            "answer_index": 0,
            "explanation": "CPython's GIL is a mutex designed to make memory management thread-safe by allowing only one native OS thread to run Python bytecode at a time."
        }
    ]

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.current_quiz = []
        self.current_index = 0
        self.user_answers = []
        self.start_time = None
        self.selected_difficulty = "All"

    def start_quiz(self, difficulty: str = "All", num_questions: int = 5) -> list[dict]:
        """
        Initializes a new randomized quiz round.
        """
        self.selected_difficulty = difficulty
        if difficulty != "All":
            pool = [q for q in self.QUESTION_BANK if q["difficulty"].lower() == difficulty.lower()]
        else:
            pool = list(self.QUESTION_BANK)

        # Select random sample
        count = min(num_questions, len(pool))
        selected = random.sample(pool, count)

        # Deep copy questions and shuffle options to prevent pattern memorization
        self.current_quiz = []
        for q in selected:
            options_copy = list(q["options"])
            correct_text = options_copy[q["answer_index"]]
            random.shuffle(options_copy)
            new_correct_idx = options_copy.index(correct_text)

            self.current_quiz.append({
                "id": q["id"],
                "topic": q["topic"],
                "difficulty": q["difficulty"],
                "question": q["question"],
                "options": options_copy,
                "answer_index": new_correct_idx,
                "explanation": q["explanation"]
            })

        self.current_index = 0
        self.user_answers = [None] * len(self.current_quiz)
        self.start_time = datetime.now()
        return self.current_quiz

    def get_current_question(self) -> dict | None:
        """Returns the active question dict or None if quiz finished."""
        if 0 <= self.current_index < len(self.current_quiz):
            return self.current_quiz[self.current_index]
        return None

    def record_answer(self, option_index: int) -> None:
        """Records user's choice for current question and moves to next."""
        if 0 <= self.current_index < len(self.current_quiz):
            self.user_answers[self.current_index] = option_index

    def next_question(self) -> bool:
        """Advances question index. Returns True if next question exists."""
        if self.current_index < len(self.current_quiz) - 1:
            self.current_index += 1
            return True
        return False

    def previous_question(self) -> bool:
        """Goes to previous question if available."""
        if self.current_index > 0:
            self.current_index -= 1
            return True
        return False

    def finish_quiz(self) -> dict:
        """
        Calculates final score, records attempt in SQLite, and returns detailed result breakdown.
        """
        total = len(self.current_quiz)
        correct_count = 0
        breakdown = []

        for q, user_ans in zip(self.current_quiz, self.user_answers):
            is_correct = (user_ans == q["answer_index"])
            if is_correct:
                correct_count += 1

            breakdown.append({
                "question": q["question"],
                "options": q["options"],
                "selected_index": user_ans,
                "correct_index": q["answer_index"],
                "is_correct": is_correct,
                "explanation": q["explanation"]
            })

        percentage = round((correct_count / total * 100), 1) if total > 0 else 0.0
        time_spent_seconds = int((datetime.now() - self.start_time).total_seconds()) if self.start_time else 0

        # Archive attempt to SQLite
        sql = """
            INSERT INTO quiz_attempts (topic, difficulty, score, total_questions, time_spent_seconds, completed_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.execute_insert(
            sql,
            ("Python Core & Data Science", self.selected_difficulty, correct_count, total, time_spent_seconds, now_str)
        )

        return {
            "score": correct_count,
            "total": total,
            "percentage": percentage,
            "time_spent_seconds": time_spent_seconds,
            "breakdown": breakdown
        }

    def get_past_attempts(self, limit: int = 10) -> list[dict]:
        """
        Retrieves historical quiz scores from SQLite.
        """
        sql = """
            SELECT * FROM quiz_attempts
            ORDER BY completed_at DESC
            LIMIT ?
        """
        attempts = self.db.fetch_all(sql, (limit,))
        for a in attempts:
            tot = a["total_questions"]
            sc = a["score"]
            a["percentage"] = round((sc / tot * 100), 1) if tot > 0 else 0.0
        return attempts
