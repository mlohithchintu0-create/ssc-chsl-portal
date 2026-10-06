# SSC CHSL 2026 Preparation Portal

> **"Practice. Improve. Crack SSC CHSL."**
> A comprehensive, modern, responsive exam preparation platform engineered strictly according to the official **Staff Selection Commission Combined Higher Secondary Level (SSC CHSL)** examination scheme.

---

## 🏛️ Official Examination Scheme & Structure

### Tier-I Computer Based Test (100 Questions)
* **Total Questions**: **Exactly 100 Questions**
* **Duration**: **60 Minutes**
* **Total Marks**: **200 Marks**
* **Marking Scheme**: **+2.00 Marks** for correct answers | **-0.50 Marks** negative marking for incorrect answers
* **Sectional Composition**:
  1. **English Language**: 25 Questions (50 Marks)
  2. **General Intelligence & Reasoning**: 25 Questions (50 Marks)
  3. **Quantitative Aptitude**: 25 Questions (50 Marks)
  4. **General Awareness**: 25 Questions (50 Marks)

---

### Tier-II Examination (135 Questions)
* **Total Objective Questions**: **Exactly 135 Questions**
* **Total Marks**: **405 Marks**
* **Marking Scheme**: **+3.00 Marks** for correct answers | **-1.00 Mark** negative marking for incorrect answers
* **Sectional Architecture**:
  * **Section-I (60 Qs | 180 Marks | 60 Minutes)**:
    * Module-I: Mathematical Abilities (30 Questions)
    * Module-II: Reasoning and General Intelligence (30 Questions)
  * **Section-II (60 Qs | 180 Marks | 60 Minutes)**:
    * Module-I: English Language and Comprehension (40 Questions)
    * Module-II: General Awareness (20 Questions)
  * **Section-III (15 Qs | 45 Marks | 15 Minutes - Qualifying)**:
    * Module-I: Computer Knowledge Test (15 Questions)

---

### Skill Test / Typing Test (Separate Practical Qualifying Module)
* **Important Notice**: The Skill/Typing test is **NOT** represented as additional MCQs. It is conducted as a separate practical examination.
* **Speed Standards**:
  * **LDC / JSA**: 35 Words Per Minute (WPM) in English or 30 WPM in Hindi (~10,500 KDPH).
  * **Data Entry Operator (DEO)**: 8,000 Key Depressions Per Hour (KDPH).
* **Live Features in Portal**:
  * Character-by-character live comparison
  * Real-time Net WPM, Gross WPM, Accuracy %, Keystrokes, Errors, and Backspaces
  * 10-Minute countdown timer with automatic completion
  * Official qualifying evaluation (Pass/Fail)

---

## 🚀 Key Portal Modules & Features

1. **All-India Mock Test Series**:
   * Timed simulations with TCS 5-status question palette (Not Visited, Not Answered, Answered, Marked for Review, Answered & Marked for Review).
   * Section switching tabs, timer warnings, clear response, and autosave on every click.
2. **Interactive Practice Arena**:
   * Immediate green/red answer highlighting.
   * Step-by-step explanations and mathematical shortcut tricks.
   * Bookmarking and question reporting.
3. **Daily Challenge Quiz**:
   * 20-question mixed quiz to build daily preparation streaks.
4. **Computer Knowledge Specialist Module**:
   * Dedicated practice for Section-III qualifying preparation.
5. **Scorecard & Analytics**:
   * Chart.js performance distribution donut charts.
   * Section-by-section accuracy breakdown, precision rates, and time analysis.
   * Solution filter tabs (All, Correct, Incorrect, Unattempted).
6. **Student Progress Dashboard**:
   * Overall preparation progress percentage.
   * Strongest and weakest subject diagnostics.
   * Mock test history and typing evaluation log.
7. **All-India Leaderboard**:
   * Aspirant rankings based on mock test scores and accuracy.
8. **Study Materials**:
   * Quantitative Aptitude Master Formula Sheet.
   * English Grammar 25 Golden Rules.
   * Computer Knowledge Exam Capsule.
9. **Admin Panel**:
   * Question Bank CRUD operations.
   * Bulk CSV / JSON question import.
   * Candidate mock activity monitor and student feedback review.

---

## 🔑 Default Credentials

| Role | Username | Password | Notes |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | Full access to question bank, imports, and candidate logs |
| **Aspirant / Student** | `aspirant` | `chsl2026` | Pre-configured aspirant profile with history |

*(Fast 1-click demo login buttons are also available on the login page)*

---

## 💻 Running the Portal Locally

```bash
# Navigate to project folder
cd C:\Users\mutch\.gemini\antigravity\scratch\ssc-chsl-portal

# Install dependencies
pip install -r requirements.txt

# Seed the database
python seed_data.py

# Run the application
python app.py
```
Open **`http://localhost:5000`** in any web browser.

---

## 🌐 Deploying to Render

1. Create a GitHub repository and push this directory.
2. Link the repository to [Render](https://render.com) as a Web Service.
3. Build Command: `pip install -r requirements.txt && python seed_data.py`
4. Start Command: `gunicorn app:app`
