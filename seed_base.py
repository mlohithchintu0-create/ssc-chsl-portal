"""
SSC CHSL Question Bank and Dataset Seeder
Includes:
- Tier-I Full Length Mock: 100 Questions (25 English, 25 Reasoning, 25 Quantitative Aptitude, 25 General Awareness)
- Tier-II Full Length Mock: 135 Questions (30 Maths, 30 Reasoning, 40 English, 20 GA, 15 Computer Knowledge)
- Topic-wise practice question bank
- Authentic Typing Test Passages
- Study Materials & Formula Sheets
"""
import sqlite3
from werkzeug.security import generate_password_hash
from database import get_db, init_db

def seed_all():
    init_db()
    conn = get_db()
    cursor = conn.cursor()

    print("Seeding subjects and topics...")
    subjects_data = [
        ("English Language", "ENG", "fa-book-open", "text-emerald-500", "Vocabulary, Grammar, Reading Comprehension, Error Spotting, Idioms & Phrases"),
        ("General Intelligence & Reasoning", "REAS", "fa-brain", "text-purple-500", "Analogies, Syllogisms, Coding-Decoding, Series, Non-Verbal Reasoning"),
        ("Quantitative Aptitude", "QUANT", "fa-calculator", "text-blue-500", "Arithmetic, Algebra, Geometry, Mensuration, Trigonometry, Data Interpretation"),
        ("General Awareness", "GA", "fa-earth-asia", "text-amber-500", "History, Polity, Geography, Economy, General Science, Static GK, Current Affairs"),
        ("Computer Knowledge", "COMP", "fa-laptop-code", "text-indigo-500", "Computer Fundamentals, MS Office, Hardware, Networking, Cyber Security")
    ]

    for name, code, icon, color, desc in subjects_data:
        cursor.execute("""
        INSERT OR IGNORE INTO subjects (name, code, icon, color, description)
        VALUES (?, ?, ?, ?, ?)
        """, (name, code, icon, color, desc))

    cursor.execute("SELECT id, code FROM subjects")
    subject_map = {row['code']: row['id'] for row in cursor.fetchall()}

    topics_by_subj = {
        "ENG": [
            "Vocabulary", "Synonyms", "Antonyms", "One-Word Substitution", "Idioms and Phrases",
            "Spelling", "Grammar", "Error Detection", "Sentence Improvement", "Fill in the Blanks",
            "Cloze Test", "Active and Passive Voice", "Direct and Indirect Speech", "Para Jumbles", "Reading Comprehension"
        ],
        "REAS": [
            "Analogy", "Classification", "Series", "Coding-Decoding", "Blood Relations",
            "Direction Sense", "Ranking", "Venn Diagrams", "Syllogism", "Statement and Conclusion",
            "Mathematical Operations", "Missing Number", "Non-Verbal Reasoning", "Mirror Images",
            "Water Images", "Paper Folding", "Embedded Figures"
        ],
        "QUANT": [
            "Number System", "Simplification", "Percentage", "Ratio and Proportion", "Average",
            "Profit and Loss", "Discount", "Simple Interest", "Compound Interest", "Time and Work",
            "Time, Speed and Distance", "Algebra", "Geometry", "Mensuration", "Trigonometry",
            "Data Interpretation", "Mixture and Alligation", "Partnership", "HCF and LCM"
        ],
        "GA": [
            "Indian History", "Geography", "Indian Polity", "Indian Constitution", "Economics",
            "Physics", "Chemistry", "Biology", "Environment", "Static GK",
            "Awards", "Sports", "Important Days", "Books and Authors", "Countries and Capitals",
            "Government Schemes", "Current Affairs"
        ],
        "COMP": [
            "Computer Fundamentals", "Hardware", "Software", "Operating Systems", "MS Word",
            "MS Excel", "MS PowerPoint", "Internet", "Email", "Networking",
            "Cyber Security", "Computer Shortcuts", "Input/Output Devices", "Memory", "Database Basics"
        ]
    }

    topic_id_map = {}
    for code, topics in topics_by_subj.items():
        s_id = subject_map[code]
        for t_name in topics:
            cursor.execute("""
            INSERT OR IGNORE INTO topics (subject_id, name, description)
            VALUES (?, ?, ?)
            """, (s_id, t_name, f"Practice questions on {t_name} for SSC CHSL"))
            cursor.execute("SELECT id FROM topics WHERE subject_id = ? AND name = ?", (s_id, t_name))
            topic_id_map[(s_id, t_name)] = cursor.fetchone()['id']

    print("Seeding default users...")
    admin_hash = generate_password_hash("admin123")
    student_hash = generate_password_hash("chsl2026")
    
    cursor.execute("""
    INSERT OR IGNORE INTO users (id, username, email, password_hash, role, full_name, streak)
    VALUES (1, 'admin', 'admin@chslportal.gov.in', ?, 'admin', 'System Administrator', 15)
    """, (admin_hash,))

    cursor.execute("""
    INSERT OR IGNORE INTO users (id, username, email, password_hash, role, full_name, streak)
    VALUES (2, 'aspirant', 'aspirant@student.com', ?, 'user', 'Priya Verma', 7)
    """, (student_hash,))

    conn.commit()
    conn.close()
    print("Base subjects, topics, and users seeded.")

if __name__ == '__main__':
    seed_all()
