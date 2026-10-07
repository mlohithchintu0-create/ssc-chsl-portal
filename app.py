import os
import json
import csv
import io
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db, init_db

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'ssc-chsl-super-secret-key-2026-portal')

# Jinja Helper filters
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d %b %Y, %I:%M %p'):
    if not value:
        return ''
    try:
        dt = datetime.fromisoformat(value)
        return dt.strftime(format)
    except Exception:
        return str(value)

def login_required(role=None):
    def decorator(f):
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to continue.', 'warning')
                return redirect(url_for('login', next=request.path))
            if role and session.get('role') != role:
                flash('You do not have administrative privileges to access that section.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

@app.context_processor
def inject_user_and_subjects():
    user = None
    subjects = []
    bookmarks_count = 0
    if 'user_id' in session:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT id, username, email, full_name, role, streak FROM users WHERE id = ?", (session['user_id'],))
        user = c.fetchone()
        c.execute("SELECT COUNT(*) as cnt FROM bookmarks WHERE user_id = ?", (session['user_id'],))
        bm = c.fetchone()
        bookmarks_count = bm['cnt'] if bm else 0
        conn.close()

    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM subjects ORDER BY id ASC")
        subjects = c.fetchall()
        conn.close()
    except Exception:
        pass

    return {
        'current_user': user,
        'all_subjects': subjects,
        'user_bookmarks_count': bookmarks_count,
        'current_year': 2026
    }

def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or '127.0.0.1'

def get_device_type():
    ua = (request.user_agent.string if request.user_agent else '').lower()
    if 'mobile' in ua or 'android' in ua or 'iphone' in ua:
        return 'Mobile'
    elif 'tablet' in ua or 'ipad' in ua:
        return 'Tablet'
    return 'Desktop'

def log_user_activity(user_id, action, details=None):
    try:
        conn = get_db()
        c = conn.cursor()
        ip = get_client_ip()
        ua = request.user_agent.string if request.user_agent else 'Unknown'
        dev = get_device_type()
        c.execute("""
        INSERT INTO user_activity_logs (user_id, action, details, ip_address, user_agent, device_type)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, action, details, ip, ua, dev))
        c.execute("""
        UPDATE users 
        SET last_active_at = CURRENT_TIMESTAMP, ip_address = ?, user_agent = ?, device_type = ?
        WHERE id = ?
        """, (ip, ua, dev, user_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging activity: {e}")

@app.before_request
def track_active_user():
    if 'user_id' in session:
        try:
            conn = get_db()
            c = conn.cursor()
            ip = get_client_ip()
            dev = get_device_type()
            c.execute("""
            UPDATE users 
            SET last_active_at = CURRENT_TIMESTAMP, ip_address = ?, device_type = ?
            WHERE id = ?
            """, (ip, dev, session['user_id']))
            conn.commit()
            conn.close()
        except Exception:
            pass

# =========================================================================
# SEPARATE AUTHENTICATION: STUDENT & ADMIN
# =========================================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    portal = request.args.get('portal', 'student')
    if request.method == 'POST':
        identifier = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        target_role = request.form.get('target_role', 'user')

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? OR email = ?", (identifier, identifier))
        user = c.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            # If user selected Admin portal, strictly require admin role
            if target_role == 'admin' and user['role'] != 'admin':
                conn.close()
                flash('Access Denied: You do not possess Administrator credentials. Please log in through the Student Portal.', 'danger')
                return render_template('login.html', active_tab='admin')

            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['full_name'] = user['full_name']

            # Update streak and last login
            today = str(date.today())
            last_login = str(user['last_login'] or '')
            new_streak = user['streak'] or 1
            if last_login and not last_login.startswith(today):
                new_streak += 1

            ip = get_client_ip()
            dev = get_device_type()
            ua = request.user_agent.string if request.user_agent else 'Unknown'

            c.execute("""
            UPDATE users 
            SET last_login = CURRENT_TIMESTAMP, last_active_at = CURRENT_TIMESTAMP, 
                streak = ?, ip_address = ?, user_agent = ?, device_type = ? 
            WHERE id = ?
            """, (new_streak, ip, ua, dev, user['id']))
            conn.commit()
            conn.close()

            log_user_activity(user['id'], "Logged In", f"Logged in via {dev} ({portal.capitalize()} Portal) from IP {ip}")

            flash(f"Welcome back, {user['full_name']}!", 'success')
            next_url = request.args.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect(url_for('admin_dashboard') if user['role'] == 'admin' else url_for('dashboard'))
        else:
            conn.close()
            flash('Invalid username/email or password.', 'danger')

    return render_template('login.html', active_tab=portal)

@app.route('/student/login')
def student_login():
    return redirect(url_for('login', portal='student'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        identifier = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE (username = ? OR email = ?)", (identifier, identifier))
        user = c.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            if user['role'] != 'admin':
                conn.close()
                flash('Access Denied: Only designated administrators can log in here.', 'danger')
                return render_template('admin/login.html')

            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = 'admin'
            session['full_name'] = user['full_name']

            ip = get_client_ip()
            dev = get_device_type()
            ua = request.user_agent.string if request.user_agent else 'Unknown'

            c.execute("""
            UPDATE users 
            SET last_login = CURRENT_TIMESTAMP, last_active_at = CURRENT_TIMESTAMP,
                ip_address = ?, user_agent = ?, device_type = ? 
            WHERE id = ?
            """, (ip, ua, dev, user['id']))
            conn.commit()
            conn.close()

            log_user_activity(user['id'], "Admin Portal Access", f"Authenticated to Administration Panel from IP {ip} ({dev})")

            flash('Welcome Administrator. System monitoring is active.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            conn.close()
            flash('Invalid administrative username or password.', 'danger')

    return render_template('admin/login.html')

@app.route('/demo-login/<role>')
def demo_login(role):
    conn = get_db()
    c = conn.cursor()
    if role == 'admin':
        c.execute("SELECT * FROM users WHERE role = 'admin' LIMIT 1")
    else:
        c.execute("SELECT * FROM users WHERE role = 'user' LIMIT 1")
    user = c.fetchone()
    conn.close()

    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        session['full_name'] = user['full_name']
        log_user_activity(user['id'], f"Demo Login ({user['role'].upper()})", f"Logged in from {get_device_type()}")
        flash(f"Logged in as {user['full_name']} ({user['role'].upper()})", 'info')
        return redirect(url_for('admin_dashboard') if user['role'] == 'admin' else url_for('dashboard'))
    flash('Demo user not found.', 'danger')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()

        if not (full_name and username and email and password):
            flash('Full name, username, email, and password are required.', 'danger')
            return render_template('register.html')

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
        if c.fetchone():
            conn.close()
            flash('Username or email already registered.', 'danger')
            return render_template('register.html')

        pw_hash = generate_password_hash(password)
        ip = get_client_ip()
        dev = get_device_type()
        ua = request.user_agent.string if request.user_agent else 'Unknown'

        c.execute("""
        INSERT INTO users (username, email, phone, password_hash, role, full_name, streak, ip_address, user_agent, device_type, last_login, last_active_at)
        VALUES (?, ?, ?, ?, 'user', ?, 1, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (username, email, phone, pw_hash, full_name, ip, ua, dev))
        conn.commit()
        new_id = c.lastrowid
        conn.close()

        session['user_id'] = new_id
        session['username'] = username
        session['role'] = 'user'
        session['full_name'] = full_name

        log_user_activity(new_id, "Account Created & Registered", f"New aspirant registered from {ip} ({dev})")

        flash('Registration successful! Welcome to the SSC CHSL Preparation Portal.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    if 'user_id' in session:
        log_user_activity(session['user_id'], "Logged Out", "Candidate ended session")
    session.clear()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('index'))

# =========================================================================
# CORE PAGES
# =========================================================================
@app.route('/')
def index():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM questions WHERE is_active = 1")
    total_questions = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM mock_tests WHERE is_published = 1")
    total_mocks = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM users")
    total_students = c.fetchone()[0]

    c.execute("SELECT * FROM mock_tests WHERE is_published = 1 ORDER BY tier ASC")
    mock_tests = c.fetchall()

    c.execute("SELECT * FROM typing_tests LIMIT 3")
    typing_tests = c.fetchall()

    conn.close()
    return render_template('index.html',
                           total_questions=total_questions,
                           total_mocks=total_mocks,
                           total_students=total_students,
                           mock_tests=mock_tests,
                           typing_tests=typing_tests)

@app.route('/tier1')
def tier1():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM mock_tests WHERE tier = 'Tier-I' AND is_published = 1")
    mocks = c.fetchall()

    # Get question counts for Tier-I subjects
    c.execute("""
    SELECT s.name, s.code, s.icon, s.color, COUNT(q.id) as q_cnt 
    FROM subjects s 
    LEFT JOIN questions q ON s.id = q.subject_id AND q.tier IN ('Tier-I', 'Both')
    WHERE s.code != 'COMP'
    GROUP BY s.id
    """)
    subject_counts = c.fetchall()
    conn.close()

    return render_template('tier1.html', mocks=mocks, subject_counts=subject_counts)

@app.route('/tier2')
def tier2():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM mock_tests WHERE tier = 'Tier-II' AND is_published = 1")
    mocks = c.fetchall()

    c.execute("""
    SELECT s.name, s.code, s.icon, s.color, COUNT(q.id) as q_cnt 
    FROM subjects s 
    LEFT JOIN questions q ON s.id = q.subject_id AND q.tier IN ('Tier-II', 'Both')
    GROUP BY s.id
    """)
    subject_counts = c.fetchall()
    conn.close()

    return render_template('tier2.html', mocks=mocks, subject_counts=subject_counts)

@app.route('/mock-tests')
def mock_tests():
    tier = request.args.get('tier', 'all')
    conn = get_db()
    c = conn.cursor()

    if tier in ('Tier-I', 'Tier-II'):
        c.execute("SELECT * FROM mock_tests WHERE tier = ? AND is_published = 1 ORDER BY id ASC", (tier,))
    else:
        c.execute("SELECT * FROM mock_tests WHERE is_published = 1 ORDER BY tier ASC, id ASC")
    mocks = c.fetchall()
    conn.close()
    return render_template('mock_tests.html', mocks=mocks, selected_tier=tier)

@app.route('/model-papers')
def model_papers():
    tier = request.args.get('tier', 'all')
    conn = get_db()
    c = conn.cursor()

    if tier in ('Tier-I', 'Tier-II'):
        c.execute("""
        SELECT * FROM mock_tests 
        WHERE (paper_type = 'model_paper' OR title LIKE '%Model Paper%') 
          AND tier = ? AND is_published = 1 
        ORDER BY id ASC
        """, (tier,))
    else:
        c.execute("""
        SELECT * FROM mock_tests 
        WHERE (paper_type = 'model_paper' OR title LIKE '%Model Paper%') 
          AND is_published = 1 
        ORDER BY tier ASC, id ASC
        """)
    papers = c.fetchall()

    c.execute("SELECT COUNT(*) FROM questions WHERE is_active = 1")
    total_q = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM mock_tests WHERE tier = 'Tier-I' AND (paper_type = 'model_paper' OR title LIKE '%Model Paper%')")
    tier1_count = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM mock_tests WHERE tier = 'Tier-II' AND (paper_type = 'model_paper' OR title LIKE '%Model Paper%')")
    tier2_count = c.fetchone()[0]

    conn.close()
    return render_template('model_papers.html',
                           papers=papers,
                           selected_tier=tier,
                           total_q=total_q,
                           tier1_count=tier1_count,
                           tier2_count=tier2_count)

@app.route('/model-paper/<int:paper_id>/solutions')
def model_paper_solutions(paper_id):
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM mock_tests WHERE id = ? AND is_published = 1", (paper_id,))
    paper = c.fetchone()
    if not paper:
        conn.close()
        flash('Model paper not found.', 'danger')
        return redirect(url_for('model_papers'))

    c.execute("""
    SELECT q.*, s.name as subject_name, s.code as subject_code, mtq.section_name, mtq.order_num
    FROM mock_test_questions mtq
    JOIN questions q ON mtq.question_id = q.id
    JOIN subjects s ON q.subject_id = s.id
    WHERE mtq.mock_test_id = ?
    ORDER BY mtq.order_num ASC
    """, (paper_id,))
    questions = c.fetchall()
    conn.close()

    return render_template('model_paper_solutions.html', paper=paper, questions=questions)

@app.route('/practice')
def practice():
    selected_subject = request.args.get('subject', 'all')
    selected_difficulty = request.args.get('difficulty', 'all')
    selected_tier = request.args.get('tier', 'all')
    page = int(request.args.get('page', 1))
    limit = 10
    offset = (page - 1) * limit

    conn = get_db()
    c = conn.cursor()

    query = "SELECT q.*, s.name as subject_name, s.code as subject_code FROM questions q JOIN subjects s ON q.subject_id = s.id WHERE q.is_active = 1"
    params = []

    if selected_subject != 'all':
        query += " AND s.code = ?"
        params.append(selected_subject)
    if selected_difficulty != 'all':
        query += " AND q.difficulty = ?"
        params.append(selected_difficulty)
    if selected_tier != 'all':
        query += " AND (q.tier = ? OR q.tier = 'Both')"
        params.append(selected_tier)

    # Count total
    count_query = query.replace("SELECT q.*, s.name as subject_name, s.code as subject_code", "SELECT COUNT(*)")
    c.execute(count_query, params)
    total_count = c.fetchone()[0]

    query += " ORDER BY q.id ASC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    c.execute(query, params)
    questions = c.fetchall()

    # Get user bookmarked question IDs
    user_bookmarks = set()
    if 'user_id' in session:
        c.execute("SELECT question_id FROM bookmarks WHERE user_id = ?", (session['user_id'],))
        user_bookmarks = {r['question_id'] for r in c.fetchall()}

    conn.close()

    total_pages = max(1, (total_count + limit - 1) // limit)

    return render_template('practice.html',
                           questions=questions,
                           total_count=total_count,
                           page=page,
                           total_pages=total_pages,
                           selected_subject=selected_subject,
                           selected_difficulty=selected_difficulty,
                           selected_tier=selected_tier,
                           user_bookmarks=user_bookmarks)

@app.route('/question-bank')
def question_bank():
    search = request.args.get('q', '').strip()
    subj = request.args.get('subject', 'all')
    conn = get_db()
    c = conn.cursor()

    query = """
    SELECT q.*, s.name as subject_name, s.code as subject_code, t.name as topic_name
    FROM questions q
    JOIN subjects s ON q.subject_id = s.id
    LEFT JOIN topics t ON q.topic_id = t.id
    WHERE q.is_active = 1
    """
    params = []
    if search:
        query += " AND (q.question_text LIKE ? OR q.explanation LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    if subj != 'all':
        query += " AND s.code = ?"
        params.append(subj)

    query += " ORDER BY q.id ASC LIMIT 50"
    c.execute(query, params)
    questions = c.fetchall()
    conn.close()

    return render_template('question_bank.html', questions=questions, search=search, selected_subject=subj)

@app.route('/pyqs')
def pyqs():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
    SELECT q.*, s.name as subject_name 
    FROM questions q
    JOIN subjects s ON q.subject_id = s.id
    WHERE q.source LIKE '%Official%' OR q.source LIKE '%PYQ%'
    ORDER BY q.id ASC
    LIMIT 30
    """)
    pyq_questions = c.fetchall()
    conn.close()
    return render_template('pyqs.html', pyq_questions=pyq_questions)

@app.route('/computer-test')
def computer_test():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM subjects WHERE code = 'COMP'")
    comp_row = c.fetchone()
    comp_id = comp_row['id'] if comp_row else 5

    c.execute("SELECT * FROM questions WHERE subject_id = ? AND is_active = 1 ORDER BY id ASC", (comp_id,))
    questions = c.fetchall()
    conn.close()
    return render_template('computer_test.html', questions=questions)

# =========================================================================
# TYPING / SKILL TEST ENGINE (PRACTICAL QUALIFYING MODULE)
# =========================================================================
@app.route('/typing-test')
def typing_test_home():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM typing_tests ORDER BY id ASC")
    tests = c.fetchall()

    user_attempts = []
    if 'user_id' in session:
        c.execute("""
        SELECT ta.*, tt.title 
        FROM typing_attempts ta 
        JOIN typing_tests tt ON ta.test_id = tt.id 
        WHERE ta.user_id = ? 
        ORDER BY ta.completed_at DESC LIMIT 5
        """, (session['user_id'],))
        user_attempts = c.fetchall()

    conn.close()
    return render_template('typing_home.html', tests=tests, user_attempts=user_attempts)

@app.route('/typing-test/<int:test_id>')
def typing_test_play(test_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM typing_tests WHERE id = ?", (test_id,))
    test = c.fetchone()
    conn.close()
    if not test:
        flash('Typing test not found.', 'danger')
        return redirect(url_for('typing_test_home'))
    return render_template('typing_play.html', test=test)

@app.route('/api/typing/submit', methods=['POST'])
def api_typing_submit():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    data = request.get_json() or {}
    test_id = data.get('test_id')
    gross_wpm = float(data.get('gross_wpm', 0))
    net_wpm = float(data.get('net_wpm', 0))
    accuracy = float(data.get('accuracy', 0))
    keystrokes = int(data.get('keystrokes', 0))
    errors = int(data.get('errors', 0))
    time_taken = int(data.get('time_taken', 600))
    # SSC CHSL standard qualifying: 35 WPM in English with >= 93% accuracy (max 7% errors for general)
    passed = 1 if (net_wpm >= 35.0 and accuracy >= 93.0) else 0

    conn = get_db()
    c = conn.cursor()
    c.execute("""
    INSERT INTO typing_attempts 
    (user_id, test_id, gross_wpm, net_wpm, accuracy, total_keystrokes, errors, time_taken_seconds, passed_qualifying)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (session['user_id'], test_id, gross_wpm, net_wpm, accuracy, keystrokes, errors, time_taken, passed))
    conn.commit()
    conn.close()

    log_user_activity(session['user_id'], "Completed Typing Test", f"Net: {net_wpm} WPM, Acc: {accuracy}%, Result: {'QUALIFIED' if passed else 'NOT QUALIFIED'}")

    return jsonify({
        'success': True,
        'net_wpm': net_wpm,
        'accuracy': accuracy,
        'passed': bool(passed),
        'message': 'Qualifying standard achieved! Excellent speed and accuracy.' if passed else 'Need practice: Aim for 35+ WPM with >93% accuracy.'
    })

# =========================================================================
# DAILY CHALLENGE / DAILY QUIZ
# =========================================================================
@app.route('/daily-quiz')
def daily_quiz():
    today_str = str(date.today())
    conn = get_db()
    c = conn.cursor()

    # Fetch 20 diverse questions for today's challenge (5 from each core subject)
    c.execute("""
    SELECT q.*, s.name as subject_name, s.code as subject_code
    FROM questions q
    JOIN subjects s ON q.subject_id = s.id
    WHERE s.code IN ('ENG', 'REAS', 'QUANT', 'GA')
    ORDER BY (q.id * 37 + ?) % 100
    LIMIT 20
    """, (datetime.now().day,))
    questions = c.fetchall()

    user_attempted = False
    if 'user_id' in session:
        c.execute("SELECT * FROM daily_quiz_attempts WHERE user_id = ? AND quiz_date = ?", (session['user_id'], today_str))
        if c.fetchone():
            user_attempted = True

    conn.close()
    return render_template('daily_quiz.html', questions=questions, today=today_str, user_attempted=user_attempted)

# =========================================================================
# FULL MOCK TEST EXAMINATION ENGINE
# =========================================================================
@app.route('/test/start/<int:mock_test_id>')
@login_required()
def start_mock_test(mock_test_id):
    user_id = session['user_id']
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM mock_tests WHERE id = ? AND is_published = 1", (mock_test_id,))
    mock = c.fetchone()
    if not mock:
        conn.close()
        flash('Mock test not found.', 'danger')
        return redirect(url_for('mock_tests'))

    # Check for in-progress attempt to restore
    c.execute("""
    SELECT * FROM test_attempts 
    WHERE user_id = ? AND mock_test_id = ? AND status = 'in_progress'
    ORDER BY start_time DESC LIMIT 1
    """, (user_id, mock_test_id))
    existing_attempt = c.fetchone()

    if existing_attempt:
        attempt_id = existing_attempt['id']
        conn.close()
        flash('Resuming your active test attempt.', 'info')
        return redirect(url_for('exam_room', attempt_id=attempt_id))

    # Fetch questions mapped to this mock test
    c.execute("""
    SELECT q.id, mtq.section_name, mtq.order_num 
    FROM mock_test_questions mtq
    JOIN questions q ON mtq.question_id = q.id
    WHERE mtq.mock_test_id = ?
    ORDER BY mtq.order_num ASC
    """, (mock_test_id,))
    mapped_questions = c.fetchall()

    if not mapped_questions:
        conn.close()
        flash('This mock test has no questions loaded yet.', 'warning')
        return redirect(url_for('mock_tests'))

    total_q = len(mapped_questions)
    max_marks = total_q * mock['marks_per_question']

    c.execute("""
    INSERT INTO test_attempts 
    (user_id, mock_test_id, mode, status, total_questions, max_marks, start_time)
    VALUES (?, ?, 'mock', 'in_progress', ?, ?, CURRENT_TIMESTAMP)
    """, (user_id, mock_test_id, total_q, max_marks))
    conn.commit()
    attempt_id = c.lastrowid

    # Initialize user_answers rows
    for item in mapped_questions:
        c.execute("""
        INSERT INTO user_answers (attempt_id, question_id, is_marked_for_review, is_submitted)
        VALUES (?, ?, 0, 0)
        """, (attempt_id, item['id']))

    conn.commit()
    conn.close()

    log_user_activity(user_id, "Started Mock Test", f"Started '{mock['title']}' ({mock['tier']})")

    return redirect(url_for('exam_room', attempt_id=attempt_id))

@app.route('/test/exam/<int:attempt_id>')
@login_required()
def exam_room(attempt_id):
    user_id = session['user_id']
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT ta.*, mt.title, mt.tier, mt.duration_minutes, mt.marks_per_question, mt.negative_marks FROM test_attempts ta JOIN mock_tests mt ON ta.mock_test_id = mt.id WHERE ta.id = ? AND ta.user_id = ?", (attempt_id, user_id))
    attempt = c.fetchone()

    if not attempt:
        conn.close()
        flash('Test attempt not found.', 'danger')
        return redirect(url_for('dashboard'))

    if attempt['status'] == 'completed':
        conn.close()
        return redirect(url_for('test_result', attempt_id=attempt_id))

    # Calculate remaining time in seconds
    c.execute("SELECT (strftime('%s', CURRENT_TIMESTAMP) - strftime('%s', start_time)) as elapsed FROM test_attempts WHERE id = ?", (attempt_id,))
    elapsed_row = c.fetchone()
    elapsed_sec = int(elapsed_row['elapsed'] or 0)
    total_allowed_sec = attempt['duration_minutes'] * 60
    remaining_sec = max(0, total_allowed_sec - elapsed_sec)

    # Fetch all questions and current answers
    c.execute("""
    SELECT 
        q.id, q.question_text, q.option_a, q.option_b, q.option_c, q.option_d,
        s.name as subject_name, s.code as subject_code,
        mtq.section_name, mtq.order_num,
        ua.selected_option, ua.is_marked_for_review, ua.time_spent_seconds
    FROM mock_test_questions mtq
    JOIN questions q ON mtq.question_id = q.id
    JOIN subjects s ON q.subject_id = s.id
    JOIN user_answers ua ON ua.question_id = q.id AND ua.attempt_id = ?
    WHERE mtq.mock_test_id = ?
    ORDER BY mtq.order_num ASC
    """, (attempt_id, attempt['mock_test_id']))
    questions = c.fetchall()
    conn.close()

    # Group sections
    sections = {}
    for q in questions:
        sec = q['section_name']
        if sec not in sections:
            sections[sec] = []
        sections[sec].append(q)

    return render_template('exam.html',
                           attempt=attempt,
                           questions=questions,
                           sections=sections,
                           remaining_sec=remaining_sec)

@app.route('/api/save-answer', methods=['POST'])
def api_save_answer():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    data = request.get_json() or {}
    attempt_id = data.get('attempt_id')
    question_id = data.get('question_id')
    selected_option = data.get('selected_option') # 'A', 'B', 'C', 'D' or None/empty
    is_review = 1 if data.get('is_marked_for_review') else 0
    time_spent = int(data.get('time_spent', 0))

    conn = get_db()
    c = conn.cursor()

    # Validate attempt belongs to session user and is in_progress
    c.execute("SELECT id FROM test_attempts WHERE id = ? AND user_id = ? AND status = 'in_progress'", (attempt_id, session['user_id']))
    if not c.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'Invalid active attempt'}), 400

    c.execute("""
    UPDATE user_answers
    SET selected_option = ?, is_marked_for_review = ?, time_spent_seconds = time_spent_seconds + ?, is_submitted = ?
    WHERE attempt_id = ? AND question_id = ?
    """, (selected_option if selected_option else None, is_review, time_spent, 1 if selected_option else 0, attempt_id, question_id))

    conn.commit()
    conn.close()

    return jsonify({'success': True})

@app.route('/test/submit/<int:attempt_id>', methods=['POST', 'GET'])
@login_required()
def submit_mock_test(attempt_id):
    user_id = session['user_id']
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT ta.*, mt.title, mt.marks_per_question, mt.negative_marks FROM test_attempts ta JOIN mock_tests mt ON ta.mock_test_id = mt.id WHERE ta.id = ? AND ta.user_id = ?", (attempt_id, user_id))
    attempt = c.fetchone()

    if not attempt or attempt['status'] == 'completed':
        conn.close()
        return redirect(url_for('test_result', attempt_id=attempt_id))

    # Evaluate answers against database correct answers
    c.execute("""
    SELECT ua.id as ans_id, ua.selected_option, q.correct_option
    FROM user_answers ua
    JOIN questions q ON ua.question_id = q.id
    WHERE ua.attempt_id = ?
    """, (attempt_id,))
    answers = c.fetchall()

    correct_count = 0
    wrong_count = 0
    attempted_count = 0

    for a in answers:
        sel = a['selected_option']
        corr = a['correct_option']
        if sel:
            attempted_count += 1
            if sel.strip().upper() == corr.strip().upper():
                correct_count += 1
                c.execute("UPDATE user_answers SET is_correct = 1 WHERE id = ?", (a['ans_id'],))
            else:
                wrong_count += 1
                c.execute("UPDATE user_answers SET is_correct = 0 WHERE id = ?", (a['ans_id'],))
        else:
            c.execute("UPDATE user_answers SET is_correct = NULL WHERE id = ?", (a['ans_id'],))

    pos_marks = correct_count * attempt['marks_per_question']
    neg_marks = wrong_count * attempt['negative_marks']
    final_score = max(0.0, pos_marks - neg_marks)
    total_q = attempt['total_questions'] or 1
    accuracy = round((correct_count / attempted_count * 100), 2) if attempted_count > 0 else 0.0
    percentage = round((final_score / attempt['max_marks'] * 100), 2) if attempt['max_marks'] > 0 else 0.0

    # Calculate actual elapsed seconds
    c.execute("SELECT (strftime('%s', CURRENT_TIMESTAMP) - strftime('%s', start_time)) as elapsed FROM test_attempts WHERE id = ?", (attempt_id,))
    elapsed_sec = int(c.fetchone()['elapsed'] or 0)

    c.execute("""
    UPDATE test_attempts
    SET status = 'completed',
        attempted = ?,
        correct_answers = ?,
        wrong_answers = ?,
        final_score = ?,
        accuracy = ?,
        percentage = ?,
        time_taken_seconds = ?,
        end_time = CURRENT_TIMESTAMP
    WHERE id = ?
    """, (attempted_count, correct_count, wrong_count, final_score, accuracy, percentage, elapsed_sec, attempt_id))

    conn.commit()
    conn.close()

    log_user_activity(user_id, "Submitted Mock Test", f"Finished '{attempt['title']}' with Score: {final_score}/{attempt['max_marks']} ({accuracy}% accuracy)")

    flash('Test submitted successfully! Here is your detailed scorecard.', 'success')
    return redirect(url_for('test_result', attempt_id=attempt_id))

@app.route('/test/result/<int:attempt_id>')
@login_required()
def test_result(attempt_id):
    user_id = session['user_id']
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    SELECT ta.*, mt.title as test_title, mt.tier, mt.duration_minutes, mt.marks_per_question, mt.negative_marks
    FROM test_attempts ta
    JOIN mock_tests mt ON ta.mock_test_id = mt.id
    WHERE ta.id = ? AND ta.user_id = ?
    """, (attempt_id, user_id))
    attempt = c.fetchone()

    if not attempt:
        conn.close()
        flash('Scorecard not found.', 'danger')
        return redirect(url_for('dashboard'))

    # Subject-wise score breakdown
    c.execute("""
    SELECT 
        s.name as subject_name,
        s.code as subject_code,
        COUNT(ua.id) as total_questions,
        COALESCE(SUM(CASE WHEN ua.selected_option IS NOT NULL THEN 1 ELSE 0 END), 0) as attempted,
        COALESCE(SUM(CASE WHEN ua.is_correct = 1 THEN 1 ELSE 0 END), 0) as correct,
        COALESCE(SUM(CASE WHEN ua.is_correct = 0 THEN 1 ELSE 0 END), 0) as wrong,
        COALESCE(SUM(ua.time_spent_seconds), 0) as time_spent
    FROM user_answers ua
    JOIN questions q ON ua.question_id = q.id
    JOIN subjects s ON q.subject_id = s.id
    WHERE ua.attempt_id = ?
    GROUP BY s.id
    ORDER BY s.id ASC
    """, (attempt_id,))
    subject_stats = c.fetchall()

    # Detailed questions review with solutions
    c.execute("""
    SELECT 
        q.*, s.name as subject_name, s.code as subject_code,
        ua.selected_option, ua.is_correct, ua.is_marked_for_review, ua.time_spent_seconds,
        mtq.section_name, mtq.order_num,
        b.id as is_bookmarked
    FROM user_answers ua
    JOIN questions q ON ua.question_id = q.id
    JOIN subjects s ON q.subject_id = s.id
    JOIN mock_test_questions mtq ON mtq.question_id = q.id AND mtq.mock_test_id = ?
    LEFT JOIN bookmarks b ON b.question_id = q.id AND b.user_id = ?
    WHERE ua.attempt_id = ?
    ORDER BY mtq.order_num ASC
    """, (attempt['mock_test_id'], user_id, attempt_id))
    solutions = c.fetchall()
    conn.close()

    return render_template('result.html',
                           attempt=attempt,
                           subject_stats=subject_stats,
                           solutions=solutions)

# =========================================================================
# DASHBOARD, PERFORMANCE & WEAK TOPICS
# =========================================================================
@app.route('/dashboard')
@login_required()
def dashboard():
    user_id = session['user_id']
    conn = get_db()
    c = conn.cursor()

    # Overall user stats
    c.execute("""
    SELECT 
        COUNT(id) as total_tests,
        COALESCE(SUM(attempted), 0) as total_attempted,
        COALESCE(SUM(correct_answers), 0) as total_correct,
        COALESCE(SUM(wrong_answers), 0) as total_wrong,
        COALESCE(MAX(final_score), 0.0) as best_score,
        COALESCE(AVG(accuracy), 0.0) as avg_accuracy,
        COALESCE(AVG(percentage), 0.0) as avg_percentage
    FROM test_attempts
    WHERE user_id = ? AND status = 'completed'
    """, (user_id,))
    stats = c.fetchone()

    # Subject performance
    c.execute("""
    SELECT 
        s.name as subject_name,
        s.code as subject_code,
        COUNT(ua.id) as total_q,
        COALESCE(SUM(CASE WHEN ua.is_correct = 1 THEN 1 ELSE 0 END), 0) as correct_q,
        COALESCE(SUM(CASE WHEN ua.is_correct = 0 THEN 1 ELSE 0 END), 0) as wrong_q
    FROM user_answers ua
    JOIN test_attempts ta ON ua.attempt_id = ta.id
    JOIN questions q ON ua.question_id = q.id
    JOIN subjects s ON q.subject_id = s.id
    WHERE ta.user_id = ? AND ta.status = 'completed' AND ua.selected_option IS NOT NULL
    GROUP BY s.id
    """, (user_id,))
    subj_perf = c.fetchall()

    # Recent test attempts
    c.execute("""
    SELECT ta.*, mt.title as test_title, mt.tier
    FROM test_attempts ta
    JOIN mock_tests mt ON ta.mock_test_id = mt.id
    WHERE ta.user_id = ? AND ta.status = 'completed'
    ORDER BY ta.end_time DESC LIMIT 5
    """, (user_id,))
    recent_tests = c.fetchall()

    # Typing test performance
    c.execute("""
    SELECT * FROM typing_attempts WHERE user_id = ? ORDER BY completed_at DESC LIMIT 3
    """, (user_id,))
    recent_typing = c.fetchall()

    conn.close()

    # Preparation score calculation
    prep_percentage = min(98, max(15, int((stats['total_attempted'] / 300.0) * 100)))

    return render_template('dashboard.html',
                           stats=stats,
                           subj_perf=subj_perf,
                           recent_tests=recent_tests,
                           recent_typing=recent_typing,
                           prep_percentage=prep_percentage)

@app.route('/bookmarks')
@login_required()
def bookmarks():
    user_id = session['user_id']
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    SELECT q.*, s.name as subject_name, b.note, b.created_at as bookmarked_at
    FROM bookmarks b
    JOIN questions q ON b.question_id = q.id
    JOIN subjects s ON q.subject_id = s.id
    WHERE b.user_id = ?
    ORDER BY b.created_at DESC
    """, (user_id,))
    items = c.fetchall()
    conn.close()

    return render_template('bookmarks.html', bookmarks=items)

@app.route('/weak-topics')
@login_required()
def weak_topics():
    user_id = session['user_id']
    conn = get_db()
    c = conn.cursor()

    # Fetch questions answered incorrectly in recent attempts
    c.execute("""
    SELECT DISTINCT q.*, s.name as subject_name, ua.time_spent_seconds
    FROM user_answers ua
    JOIN test_attempts ta ON ua.attempt_id = ta.id
    JOIN questions q ON ua.question_id = q.id
    JOIN subjects s ON q.subject_id = s.id
    WHERE ta.user_id = ? AND ua.is_correct = 0
    ORDER BY ua.id DESC LIMIT 30
    """, (user_id,))
    wrong_questions = c.fetchall()
    conn.close()

    return render_template('weak_topics.html', questions=wrong_questions)

@app.route('/leaderboard')
def leaderboard():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    SELECT 
        u.id, u.full_name, u.username, u.streak,
        COUNT(ta.id) as tests_completed,
        COALESCE(MAX(ta.final_score), 0.0) as highest_score,
        COALESCE(AVG(ta.accuracy), 0.0) as avg_accuracy
    FROM users u
    JOIN test_attempts ta ON u.id = ta.user_id
    WHERE ta.status = 'completed'
    GROUP BY u.id
    ORDER BY highest_score DESC, avg_accuracy DESC
    LIMIT 20
    """)
    leaders = c.fetchall()
    conn.close()

    return render_template('leaderboard.html', leaders=leaders)

@app.route('/study-material')
def study_material():
    cat = request.args.get('category', 'all')
    conn = get_db()
    c = conn.cursor()

    query = "SELECT sm.*, s.name as subject_name FROM study_materials sm JOIN subjects s ON sm.subject_id = s.id"
    params = []
    if cat != 'all':
        query += " WHERE sm.category = ?"
        params.append(cat)
    query += " ORDER BY sm.id ASC"

    c.execute(query, params)
    materials = c.fetchall()
    conn.close()

    return render_template('study_material.html', materials=materials, selected_cat=cat)

@app.route('/study-material/<int:mat_id>')
def study_material_detail(mat_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT sm.*, s.name as subject_name FROM study_materials sm JOIN subjects s ON sm.subject_id = s.id WHERE sm.id = ?", (mat_id,))
    mat = c.fetchone()
    conn.close()

    if not mat:
        flash('Material not found.', 'danger')
        return redirect(url_for('study_material'))

    return render_template('study_material_detail.html', material=mat)

# =========================================================================
# AJAX APIS: BOOKMARK & REPORT
# =========================================================================
@app.route('/api/bookmark/toggle', methods=['POST'])
def api_toggle_bookmark():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login to bookmark'}), 401

    data = request.get_json() or {}
    q_id = data.get('question_id')
    user_id = session['user_id']

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM bookmarks WHERE user_id = ? AND question_id = ?", (user_id, q_id))
    existing = c.fetchone()

    if existing:
        c.execute("DELETE FROM bookmarks WHERE id = ?", (existing['id'],))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'bookmarked': False, 'message': 'Question removed from bookmarks'})
    else:
        c.execute("INSERT INTO bookmarks (user_id, question_id) VALUES (?, ?)", (user_id, q_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'bookmarked': True, 'message': 'Question saved to your bookmarks!'})

@app.route('/api/report-question', methods=['POST'])
def api_report_question():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login to report'}), 401

    data = request.get_json() or {}
    q_id = data.get('question_id')
    issue_type = data.get('issue_type', 'Typo/Error')
    details = data.get('details', '')

    conn = get_db()
    c = conn.cursor()
    c.execute("""
    INSERT INTO question_reports (user_id, question_id, issue_type, details)
    VALUES (?, ?, ?, ?)
    """, (session['user_id'], q_id, issue_type, details))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Thank you! Your feedback has been sent to our faculty for review.'})

# =========================================================================
# ADMIN PANEL & STUDENT MONITORING
# =========================================================================
@app.route('/admin')
@login_required(role='admin')
def admin_dashboard():
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM questions")
    total_q = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM mock_tests")
    total_mocks = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM users WHERE role = 'user'")
    total_users = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM test_attempts WHERE status = 'completed'")
    total_attempts = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM question_reports WHERE status = 'pending'")
    pending_reports = c.fetchone()[0]

    # Count online students (active in the last 15 minutes)
    c.execute("""
    SELECT COUNT(*) FROM users 
    WHERE role = 'user' AND last_active_at >= datetime('now', '-15 minutes')
    """)
    online_count = c.fetchone()[0]

    # Real-Time Student Activity Stream
    c.execute("""
    SELECT al.*, u.full_name, u.username, u.email
    FROM user_activity_logs al
    JOIN users u ON al.user_id = u.id
    ORDER BY al.created_at DESC
    LIMIT 20
    """)
    recent_activities = c.fetchall()

    # Recent Mock Attempts
    c.execute("""
    SELECT ta.*, u.full_name, mt.title as test_title
    FROM test_attempts ta
    JOIN users u ON ta.user_id = u.id
    JOIN mock_tests mt ON ta.mock_test_id = mt.id
    WHERE ta.status = 'completed'
    ORDER BY ta.end_time DESC LIMIT 8
    """)
    recent_attempts = c.fetchall()

    conn.close()

    return render_template('admin/dashboard.html',
                           total_q=total_q,
                           total_mocks=total_mocks,
                           total_users=total_users,
                           total_attempts=total_attempts,
                           pending_reports=pending_reports,
                           online_count=online_count,
                           recent_activities=recent_activities,
                           recent_attempts=recent_attempts)

@app.route('/admin/students')
@login_required(role='admin')
def admin_students():
    search = request.args.get('q', '').strip()
    conn = get_db()
    c = conn.cursor()

    query = """
    SELECT 
        u.*,
        COUNT(DISTINCT ta.id) as tests_completed,
        COALESCE(MAX(ta.final_score), 0.0) as best_score,
        COALESCE(AVG(ta.accuracy), 0.0) as avg_accuracy,
        COUNT(DISTINCT tya.id) as typing_completed,
        CASE 
            WHEN u.last_active_at >= datetime('now', '-15 minutes') THEN 1
            ELSE 0
        END as is_online_now
    FROM users u
    LEFT JOIN test_attempts ta ON u.id = ta.user_id AND ta.status = 'completed'
    LEFT JOIN typing_attempts tya ON u.id = tya.user_id
    WHERE u.role = 'user'
    """
    params = []
    if search:
        query += " AND (u.full_name LIKE ? OR u.username LIKE ? OR u.email LIKE ? OR u.phone LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"])

    query += " GROUP BY u.id ORDER BY is_online_now DESC, u.last_active_at DESC"

    c.execute(query, params)
    students = c.fetchall()
    conn.close()

    return render_template('admin/students.html', students=students, search=search)

@app.route('/admin/students/<int:student_id>')
@login_required(role='admin')
def admin_student_detail(student_id):
    conn = get_db()
    c = conn.cursor()

    # Student metadata
    c.execute("""
    SELECT 
        u.*,
        CASE 
            WHEN u.last_active_at >= datetime('now', '-15 minutes') THEN 1
            ELSE 0
        END as is_online_now
    FROM users u 
    WHERE u.id = ? AND u.role = 'user'
    """, (student_id,))
    student = c.fetchone()

    if not student:
        conn.close()
        flash('Student record not found.', 'danger')
        return redirect(url_for('admin_students'))

    # All Mock Test Attempts
    c.execute("""
    SELECT ta.*, mt.title as test_title, mt.tier
    FROM test_attempts ta
    JOIN mock_tests mt ON ta.mock_test_id = mt.id
    WHERE ta.user_id = ?
    ORDER BY ta.start_time DESC
    """, (student_id,))
    attempts = c.fetchall()

    # All Typing Attempts
    c.execute("""
    SELECT tya.*, tt.title as passage_title
    FROM typing_attempts tya
    JOIN typing_tests tt ON tya.test_id = tt.id
    WHERE tya.user_id = ?
    ORDER BY tya.completed_at DESC
    """, (student_id,))
    typing_records = c.fetchall()

    # Chronological Audit Activity Log
    c.execute("""
    SELECT * FROM user_activity_logs
    WHERE user_id = ?
    ORDER BY created_at DESC
    LIMIT 50
    """, (student_id,))
    activity_logs = c.fetchall()

    conn.close()

    return render_template('admin/student_detail.html',
                           student=student,
                           attempts=attempts,
                           typing_records=typing_records,
                           activity_logs=activity_logs)

@app.route('/admin/questions')
@login_required(role='admin')
def admin_questions():
    search = request.args.get('q', '').strip()
    subj = request.args.get('subject', 'all')
    page = int(request.args.get('page', 1))
    limit = 20
    offset = (page - 1) * limit

    conn = get_db()
    c = conn.cursor()

    query = "SELECT q.*, s.name as subject_name FROM questions q JOIN subjects s ON q.subject_id = s.id WHERE 1=1"
    params = []
    if search:
        query += " AND q.question_text LIKE ?"
        params.append(f"%{search}%")
    if subj != 'all':
        query += " AND s.code = ?"
        params.append(subj)

    count_q = query.replace("SELECT q.*, s.name as subject_name", "SELECT COUNT(*)")
    c.execute(count_q, params)
    total_count = c.fetchone()[0]

    query += " ORDER BY q.id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    c.execute(query, params)
    questions = c.fetchall()
    conn.close()

    total_pages = max(1, (total_count + limit - 1) // limit)

    return render_template('admin/questions.html',
                           questions=questions,
                           total_count=total_count,
                           page=page,
                           total_pages=total_pages,
                           search=search,
                           selected_subj=subj)

@app.route('/admin/questions/add', methods=['GET', 'POST'])
@login_required(role='admin')
def admin_add_question():
    conn = get_db()
    c = conn.cursor()

    if request.method == 'POST':
        subject_id = int(request.form.get('subject_id'))
        tier = request.form.get('tier', 'Tier-I')
        difficulty = request.form.get('difficulty', 'Medium')
        question_text = request.form.get('question_text', '').strip()
        option_a = request.form.get('option_a', '').strip()
        option_b = request.form.get('option_b', '').strip()
        option_c = request.form.get('option_c', '').strip()
        option_d = request.form.get('option_d', '').strip()
        correct_option = request.form.get('correct_option', 'A').strip().upper()
        explanation = request.form.get('explanation', '').strip()
        shortcut = request.form.get('shortcut', '').strip()

        c.execute("""
        INSERT INTO questions 
        (subject_id, tier, difficulty, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, shortcut, year)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 2026)
        """, (subject_id, tier, difficulty, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, shortcut))
        conn.commit()
        conn.close()

        flash('New question successfully added to the question bank!', 'success')
        return redirect(url_for('admin_questions'))

    c.execute("SELECT * FROM subjects ORDER BY id ASC")
    subjects = c.fetchall()
    conn.close()
    return render_template('admin/question_form.html', subjects=subjects, question=None)

@app.route('/admin/questions/delete/<int:q_id>', methods=['POST'])
@login_required(role='admin')
def admin_delete_question(q_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM questions WHERE id = ?", (q_id,))
    conn.commit()
    conn.close()
    flash(f'Question #{q_id} deleted.', 'info')
    return redirect(url_for('admin_questions'))

@app.route('/admin/questions/import', methods=['GET', 'POST'])
@login_required(role='admin')
def admin_import_questions():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or not file.filename:
            flash('Please select a valid CSV or JSON file.', 'danger')
            return redirect(url_for('admin_import_questions'))

        content = file.read().decode('utf-8', errors='ignore')
        imported_count = 0
        conn = get_db()
        c = conn.cursor()

        c.execute("SELECT id, code FROM subjects")
        s_map = {r['code']: r['id'] for r in c.fetchall()}

        try:
            if file.filename.endswith('.json'):
                data = json.loads(content)
                for item in data:
                    subj_id = s_map.get(item.get('subject_code', 'ENG'), 1)
                    c.execute("""
                    INSERT INTO questions (subject_id, tier, difficulty, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, shortcut, year)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 2026)
                    """, (
                        subj_id,
                        item.get('tier', 'Tier-I'),
                        item.get('difficulty', 'Medium'),
                        item['question_text'],
                        item['option_a'],
                        item['option_b'],
                        item['option_c'],
                        item['option_d'],
                        item['correct_option'],
                        item.get('explanation', ''),
                        item.get('shortcut', '')
                    ))
                    imported_count += 1
            else: # CSV
                csv_reader = csv.DictReader(io.StringIO(content))
                for row in csv_reader:
                    subj_id = s_map.get(row.get('subject_code', 'ENG'), 1)
                    c.execute("""
                    INSERT INTO questions (subject_id, tier, difficulty, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, shortcut, year)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 2026)
                    """, (
                        subj_id,
                        row.get('tier', 'Tier-I'),
                        row.get('difficulty', 'Medium'),
                        row['question_text'],
                        row['option_a'],
                        row['option_b'],
                        row['option_c'],
                        row['option_d'],
                        row['correct_option'],
                        row.get('explanation', ''),
                        row.get('shortcut', '')
                    ))
                    imported_count += 1

            conn.commit()
            conn.close()
            flash(f'Successfully imported {imported_count} questions into the bank!', 'success')
            return redirect(url_for('admin_questions'))
        except Exception as e:
            conn.close()
            flash(f'Import failed: {str(e)}', 'danger')

    return render_template('admin/import.html')

@app.route('/admin/reports')
@login_required(role='admin')
def admin_reports():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
    SELECT qr.*, q.question_text, u.username 
    FROM question_reports qr
    JOIN questions q ON qr.question_id = q.id
    JOIN users u ON qr.user_id = u.id
    ORDER BY qr.created_at DESC
    """)
    reports = c.fetchall()
    conn.close()
    return render_template('admin/reports.html', reports=reports)

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
