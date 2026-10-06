import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ssc_chsl.db')

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user', -- 'admin' or 'user'
        full_name TEXT NOT NULL,
        phone TEXT,
        ip_address TEXT,
        user_agent TEXT,
        device_type TEXT,
        streak INTEGER DEFAULT 1,
        last_login DATETIME,
        last_active_at DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Alter table if existing database doesn't have the new columns yet
    existing_user_cols = [row[1] for row in cursor.execute("PRAGMA table_info(users)").fetchall()]
    for col, col_type in [
        ('phone', 'TEXT'),
        ('ip_address', 'TEXT'),
        ('user_agent', 'TEXT'),
        ('device_type', 'TEXT'),
        ('last_active_at', 'DATETIME')
    ]:
        if col not in existing_user_cols:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {col_type}")

    # Activity Logs Table (For Admin Live Student Monitoring)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        details TEXT,
        ip_address TEXT,
        user_agent TEXT,
        device_type TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_user ON user_activity_logs(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_time ON user_activity_logs(created_at);")

    # 2. Subjects Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        code TEXT UNIQUE NOT NULL, -- 'ENG', 'REAS', 'QUANT', 'GA', 'COMP'
        icon TEXT,
        color TEXT,
        description TEXT
    );
    """)

    # 3. Topics Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
        UNIQUE (subject_id, name)
    );
    """)

    # 4. Questions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER NOT NULL,
        topic_id INTEGER,
        tier TEXT NOT NULL DEFAULT 'Tier-I', -- 'Tier-I', 'Tier-II', 'Both'
        difficulty TEXT NOT NULL DEFAULT 'Medium', -- 'Easy', 'Medium', 'Hard'
        question_text TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct_option TEXT NOT NULL, -- 'A', 'B', 'C', 'D'
        explanation TEXT NOT NULL,
        shortcut TEXT,
        year INTEGER,
        source TEXT DEFAULT 'SSC CHSL Question Bank',
        is_active INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
        FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE SET NULL
    );
    """)

    # 5. Mock Tests Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mock_tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        tier TEXT NOT NULL, -- 'Tier-I' or 'Tier-II'
        total_questions INTEGER NOT NULL,
        duration_minutes INTEGER NOT NULL,
        total_marks REAL NOT NULL,
        marks_per_question REAL NOT NULL,
        negative_marks REAL NOT NULL,
        instructions TEXT,
        is_published INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 6. Mock Test Questions Mapping
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mock_test_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mock_test_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        section_name TEXT NOT NULL,
        order_num INTEGER NOT NULL,
        FOREIGN KEY (mock_test_id) REFERENCES mock_tests(id) ON DELETE CASCADE,
        FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
    );
    """)

    # 7. Test Attempts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS test_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        mock_test_id INTEGER,
        mode TEXT NOT NULL DEFAULT 'mock', -- 'mock', 'practice', 'daily_quiz', 'topic_practice', 'weak_topics'
        status TEXT NOT NULL DEFAULT 'in_progress', -- 'in_progress', 'completed'
        total_questions INTEGER NOT NULL DEFAULT 0,
        attempted INTEGER DEFAULT 0,
        correct_answers INTEGER DEFAULT 0,
        wrong_answers INTEGER DEFAULT 0,
        final_score REAL DEFAULT 0.0,
        max_marks REAL DEFAULT 0.0,
        accuracy REAL DEFAULT 0.0,
        percentage REAL DEFAULT 0.0,
        time_taken_seconds INTEGER DEFAULT 0,
        start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        end_time DATETIME,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (mock_test_id) REFERENCES mock_tests(id) ON DELETE SET NULL
    );
    """)

    # 8. User Answers Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attempt_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        selected_option TEXT,
        is_correct INTEGER,
        is_marked_for_review INTEGER DEFAULT 0,
        is_submitted INTEGER DEFAULT 0,
        time_spent_seconds INTEGER DEFAULT 0,
        FOREIGN KEY (attempt_id) REFERENCES test_attempts(id) ON DELETE CASCADE,
        FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
    );
    """)

    # 9. Bookmarks Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookmarks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        note TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
        UNIQUE (user_id, question_id)
    );
    """)

    # 10. Question Reports Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS question_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        issue_type TEXT NOT NULL,
        details TEXT,
        status TEXT DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
    );
    """)

    # 11. Daily Quiz Attempts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_quiz_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        quiz_date TEXT NOT NULL,
        score REAL NOT NULL,
        total_questions INTEGER NOT NULL,
        time_spent INTEGER NOT NULL,
        completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE (user_id, quiz_date)
    );
    """)

    # 12. Typing Tests Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS typing_tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        target_wpm INTEGER DEFAULT 35,
        duration_minutes INTEGER DEFAULT 10,
        text_content TEXT NOT NULL,
        difficulty TEXT DEFAULT 'Standard'
    );
    """)

    # 13. Typing Attempts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS typing_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        test_id INTEGER NOT NULL,
        gross_wpm REAL NOT NULL,
        net_wpm REAL NOT NULL,
        accuracy REAL NOT NULL,
        total_keystrokes INTEGER NOT NULL,
        errors INTEGER NOT NULL,
        time_taken_seconds INTEGER NOT NULL,
        passed_qualifying INTEGER DEFAULT 0,
        completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (test_id) REFERENCES typing_tests(id) ON DELETE CASCADE
    );
    """)

    # 14. Study Materials Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS study_materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        subject_id INTEGER NOT NULL,
        category TEXT NOT NULL, -- 'Formula Sheet', 'Grammar Rules', 'Shortcut Tricks', 'GK Capsule'
        summary TEXT,
        content TEXT NOT NULL,
        tags TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
    );
    """)

    # Create indexes for optimal querying speed
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_subj ON questions(subject_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_tier ON questions(tier);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_test_attempts_user ON test_attempts(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_answers_attempt ON user_answers(attempt_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bookmarks_user ON bookmarks(user_id);")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("SSC CHSL Database initialized successfully with all tables and indexes.")
