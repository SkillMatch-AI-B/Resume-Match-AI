import sqlite3
import os

# Point to the database file we just created
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "app.db")

def get_connection():
    """Helper function to get a database connection that returns dictionary-like rows."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This lets us access columns by name (e.g., row['email'])
    return conn

# ==========================================
# USER AUTHENTICATION & REGISTRATION
# ==========================================

def get_user_by_email(email):
    """Fetches a user by their email address."""
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return dict(user) if user else None

def create_user(email, password, role):
    """Registers a new user. Returns True if successful, False if email exists."""
    conn = get_connection()
    try:
        conn.execute("INSERT INTO users (email, password, role) VALUES (?, ?, ?)", (email, password, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Email already exists
        return False
    finally:
        conn.close()

# ==========================================
# JOB SEEKER QUERIES
# ==========================================

def save_report(user_id, job_title, match_score, missing_skills, ai_feedback):
    """Saves a generated resume report to the Job Seeker's history."""
    conn = get_connection()
    conn.execute('''
        INSERT INTO reports (user_id, job_title, match_score, missing_skills, ai_feedback)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, job_title, match_score, missing_skills, ai_feedback))
    conn.commit()
    conn.close()

def get_user_reports(user_id):
    """Fetches all past reports for a specific Job Seeker."""
    conn = get_connection()
    reports = conn.execute("SELECT * FROM reports WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
    conn.close()
    return [dict(row) for row in reports]

# ==========================================
# RECRUITER QUERIES
# ==========================================

def create_job(recruiter_id, title, description):
    """Creates a new Job Campaign for a recruiter."""
    conn = get_connection()
    conn.execute("INSERT INTO jobs (recruiter_id, title, description) VALUES (?, ?, ?)", (recruiter_id, title, description))
    conn.commit()
    conn.close()

def get_recruiter_jobs(recruiter_id):
    """Fetches all active Job Campaigns created by a specific recruiter."""
    conn = get_connection()
    jobs = conn.execute("SELECT * FROM jobs WHERE recruiter_id = ? ORDER BY created_at DESC", (recruiter_id,)).fetchall()
    conn.close()
    return [dict(row) for row in jobs]

def add_candidate(job_id, resume_name, match_score, skills_found):
    """Saves a matched candidate's resume score to a specific Job Campaign."""
    conn = get_connection()
    conn.execute('''
        INSERT INTO candidates (job_id, resume_name, match_score, skills_found)
        VALUES (?, ?, ?, ?)
    ''', (job_id, resume_name, match_score, skills_found))
    conn.commit()
    conn.close()

def get_job_candidates(job_id):
    """Fetches and ranks all candidates for a specific Job Campaign."""
    conn = get_connection()
    candidates = conn.execute("SELECT * FROM candidates WHERE job_id = ? ORDER BY match_score DESC", (job_id,)).fetchall()
    conn.close()
    return [dict(row) for row in candidates]

# ==========================================
# ADMIN QUERIES
# ==========================================

def get_all_users():
    """Fetches all registered users for the Admin dashboard."""
    conn = get_connection()
    users = conn.execute("SELECT id, email, role, created_at FROM users ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(row) for row in users]

def get_all_skills():
    """Returns a hardcoded list of skills since the Admin database was removed."""
    # This list ensures your BERT engine still has a baseline to compare against
    return [
        "Python", "Java", "JavaScript", "React", "Django", "SQL", "AWS", 
        "Docker", "Kubernetes", "C++", "Spring Boot", "Machine Learning", 
        "Data Analysis", "Project Management", "Agile", "REST APIs"
    ]

def add_skill(skill_name):
    """Adds a new skill to the master database."""
    conn = get_connection()
    try:
        conn.execute("INSERT INTO skills (skill_name) VALUES (?)", (skill_name,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Skill already exists
    finally:
        conn.close()

def delete_report(report_id):
    """Deletes a specific job seeker report from the database."""
    # REPLACE the line below with whatever the rest of your file uses!
    conn = sqlite3.connect('database/app.db') 
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))
    conn.commit()
    conn.close()

def delete_candidate(candidate_id):
    """Deletes a specific candidate from a recruiter's campaign."""
    # REPLACE the line below with whatever the rest of your file uses!
    conn = sqlite3.connect('database/app.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
    conn.commit()
    conn.close()      