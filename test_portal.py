import unittest
import json
from app import app
from database import get_db, init_db

class TestSSCCHSLPortal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        cls.client = app.test_client()

    def test_01_database_structure(self):
        conn = get_db()
        c = conn.cursor()
        
        # Check mock tests
        c.execute("SELECT id, title, tier, total_questions FROM mock_tests")
        mocks = c.fetchall()
        self.assertEqual(len(mocks), 2)
        
        # Tier-I mock must have exactly 100 questions
        tier1_mock = next(m for m in mocks if m['tier'] == 'Tier-I')
        self.assertEqual(tier1_mock['total_questions'], 100)
        c.execute("SELECT COUNT(*) FROM mock_test_questions WHERE mock_test_id = ?", (tier1_mock['id'],))
        self.assertEqual(c.fetchone()[0], 100)

        # Tier-II mock must have exactly 135 questions
        tier2_mock = next(m for m in mocks if m['tier'] == 'Tier-II')
        self.assertEqual(tier2_mock['total_questions'], 135)
        c.execute("SELECT COUNT(*) FROM mock_test_questions WHERE mock_test_id = ?", (tier2_mock['id'],))
        self.assertEqual(c.fetchone()[0], 135)

        # Check typing tests
        c.execute("SELECT COUNT(*) FROM typing_tests")
        self.assertGreaterEqual(c.fetchone()[0], 3)

        # Check study materials
        c.execute("SELECT COUNT(*) FROM study_materials")
        self.assertGreaterEqual(c.fetchone()[0], 3)
        conn.close()

    def test_02_public_pages(self):
        endpoints = [
            '/',
            '/tier1',
            '/tier2',
            '/mock-tests',
            '/practice',
            '/daily-quiz',
            '/computer-test',
            '/typing-test',
            '/pyqs',
            '/question-bank',
            '/leaderboard',
            '/study-material',
            '/login',
            '/register'
        ]
        for ep in endpoints:
            res = self.client.get(ep)
            self.assertEqual(res.status_code, 200, f"Endpoint {ep} failed with status {res.status_code}")

    def test_03_login_and_dashboard(self):
        # Demo login as student
        res = self.client.get('/demo-login/user', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Student Preparation Dashboard", res.data)

        # Check dashboard metrics
        res = self.client.get('/dashboard')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Overall Preparation Progress", res.data)

    def test_04_exam_simulation_lifecycle(self):
        # Login
        self.client.get('/demo-login/user', follow_redirects=True)

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT id FROM mock_tests WHERE tier = 'Tier-I' LIMIT 1")
        mock_id = c.fetchone()['id']
        conn.close()

        # Start Tier-I Mock test
        res = self.client.get(f'/test/start/{mock_id}', follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Extract attempt ID from current user's active attempt
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT id FROM test_attempts WHERE user_id = 2 ORDER BY id DESC LIMIT 1")
        attempt_id = c.fetchone()['id']

        # Save an answer via AJAX
        c.execute("SELECT question_id FROM mock_test_questions WHERE mock_test_id = ? LIMIT 1", (mock_id,))
        q_id = c.fetchone()['question_id']
        conn.close()

        save_res = self.client.post('/api/save-answer',
            data=json.dumps({
                'attempt_id': attempt_id,
                'question_id': q_id,
                'selected_option': 'B',
                'is_marked_for_review': 0,
                'time_spent': 15
            }),
            content_type='application/json'
        )
        self.assertEqual(save_res.status_code, 200)

        # Submit test
        submit_res = self.client.post(f'/test/submit/{attempt_id}', follow_redirects=True)
        self.assertEqual(submit_res.status_code, 200)
        self.assertIn(b"Official Exam Scorecard", submit_res.data)

    def test_05_typing_test_engine(self):
        self.client.get('/demo-login/user', follow_redirects=True)

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT id FROM typing_tests LIMIT 1")
        test_id = c.fetchone()['id']
        conn.close()

        # Play typing test
        res = self.client.get(f'/typing-test/{test_id}')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Official Typing Assessment", res.data)

        # Submit typing result API
        api_res = self.client.post('/api/typing/submit',
            data=json.dumps({
                'test_id': test_id,
                'gross_wpm': 38.5,
                'net_wpm': 36.2,
                'accuracy': 95.5,
                'keystrokes': 1800,
                'errors': 3,
                'time_taken': 600
            }),
            content_type='application/json'
        )
        self.assertEqual(api_res.status_code, 200)
        data = json.loads(api_res.data)
        self.assertTrue(data['success'])
        self.assertTrue(data['passed'])

    def test_06_bookmark_and_report_apis(self):
        self.client.get('/demo-login/user', follow_redirects=True)

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT id FROM questions LIMIT 1")
        q_id = c.fetchone()['id']
        conn.close()

        # Bookmark toggle
        bm_res = self.client.post('/api/bookmark/toggle',
            data=json.dumps({'question_id': q_id}),
            content_type='application/json'
        )
        self.assertEqual(bm_res.status_code, 200)
        data = json.loads(bm_res.data)
        self.assertTrue(data['success'])

        # Report question
        rep_res = self.client.post('/api/report-question',
            data=json.dumps({
                'question_id': q_id,
                'issue_type': 'Typo',
                'details': 'Small typo verification test'
            }),
            content_type='application/json'
        )
        self.assertEqual(rep_res.status_code, 200)

    def test_07_admin_controls(self):
        # Demo login as admin
        self.client.get('/demo-login/admin', follow_redirects=True)

        res = self.client.get('/admin')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Admin Control Center", res.data)

        # Questions listing
        res = self.client.get('/admin/questions')
        self.assertEqual(res.status_code, 200)

        # Add question
        add_res = self.client.post('/admin/questions/add', data={
            'subject_id': 1,
            'tier': 'Tier-I',
            'difficulty': 'Easy',
            'question_text': 'Unit Test Question for SSC CHSL?',
            'option_a': 'Option 1',
            'option_b': 'Option 2',
            'option_c': 'Option 3',
            'option_d': 'Option 4',
            'correct_option': 'B',
            'explanation': 'This is a test explanation.',
            'shortcut': 'Test shortcut'
        }, follow_redirects=True)
        self.assertEqual(add_res.status_code, 200)
        self.assertIn(b"New question successfully added", add_res.data)

if __name__ == '__main__':
    unittest.main()
