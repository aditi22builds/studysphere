-- ==============================================================================
-- STUDYSPHERE DATABASE SCHEMA
-- Relational Schema for Academic Productivity Management
-- Designed for SQLite with Foreign Key Support
-- ==============================================================================

PRAGMA foreign_keys = ON;

-- 1. SUBJECTS TABLE
-- Stores academic course subjects tracked by the student.
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    code TEXT NOT NULL,
    color TEXT NOT NULL DEFAULT '#8B5CF6',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. TASKS TABLE
-- Stores academic assignments, lab submissions, exam preps, and personal study tasks.
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT NOT NULL CHECK(priority IN ('Low', 'Medium', 'High')) DEFAULT 'Medium',
    due_date TEXT NOT NULL, -- Format: YYYY-MM-DD
    status TEXT NOT NULL CHECK(status IN ('Pending', 'In Progress', 'Completed')) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE SET NULL
);

-- 3. STUDY SESSIONS TABLE
-- Logs completed Pomodoro focus intervals and break sessions for productivity analytics.
CREATE TABLE IF NOT EXISTS study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER,
    duration_minutes REAL NOT NULL,
    session_type TEXT NOT NULL CHECK(session_type IN ('Focus', 'Short Break', 'Long Break')) DEFAULT 'Focus',
    notes TEXT,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE SET NULL
);

-- 4. NOTES TABLE
-- Holds lecture notes, formula sheets, quick code snippets, and study summaries.
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT, -- Comma-separated tags, e.g. "algorithms,trees,exam"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE SET NULL
);

-- 5. QUIZ ATTEMPTS TABLE
-- Archives student Python knowledge assessment results for skill progression tracking.
CREATE TABLE IF NOT EXISTS quiz_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    score INTEGER NOT NULL,
    total_questions INTEGER NOT NULL,
    time_spent_seconds INTEGER NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create performance indexes for frequent query patterns (due dates, completion status, timestamps)
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_study_sessions_completed ON study_sessions(completed_at);
CREATE INDEX IF NOT EXISTS idx_notes_subject ON notes(subject_id);
