import sqlite3
import os

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "app.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    return conn

# ==========================================
# USER AUTHENTICATION & REGISTRATION
# ==========================================

def get_user_by_email(email):
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return dict(user) if user else None

def create_user(email, password, role):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO users (email, password, role) VALUES (?, ?, ?)", (email, password, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# ==========================================
# JOB SEEKER QUERIES (Uses content_hash)
# ==========================================

def save_report(user_id, resume_name, job_title, match_score, missing_skills, ai_feedback, content_hash):
    conn = get_connection()
    conn.execute('''
        INSERT INTO reports (user_id, resume_name, job_title, match_score, missing_skills, ai_feedback, content_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, resume_name, job_title, match_score, missing_skills, ai_feedback, content_hash))
    conn.commit()
    conn.close()

def get_user_reports(user_id):
    conn = get_connection()
    reports = conn.execute("SELECT * FROM reports WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
    conn.close()
    return [dict(row) for row in reports]

def check_existing_report(user_id, job_title, content_hash):
    conn = get_connection()
    res = conn.execute("SELECT id FROM reports WHERE user_id = ? AND job_title = ? AND content_hash = ?", (user_id, job_title, content_hash)).fetchone()
    conn.close()
    return res if res else None

# ==========================================
# RECRUITER QUERIES (Reverted back to normal, NO Hash)
# ==========================================

def create_job(recruiter_id, title, description):
    conn = get_connection()
    conn.execute("INSERT INTO jobs (recruiter_id, title, description) VALUES (?, ?, ?)", (recruiter_id, title, description))
    conn.commit()
    conn.close()

def get_recruiter_jobs(recruiter_id):
    conn = get_connection()
    jobs = conn.execute("SELECT * FROM jobs WHERE recruiter_id = ? ORDER BY created_at DESC", (recruiter_id,)).fetchall()
    conn.close()
    return [dict(row) for row in jobs]

def add_candidate(job_id, resume_name, match_score, skills_found):
    conn = get_connection()
    conn.execute('''
        INSERT INTO candidates (job_id, resume_name, match_score, skills_found)
        VALUES (?, ?, ?, ?)
    ''', (job_id, resume_name, match_score, skills_found))
    conn.commit()
    conn.close()

def get_job_candidates(job_id):
    conn = get_connection()
    candidates = conn.execute("SELECT * FROM candidates WHERE job_id = ? ORDER BY match_score DESC", (job_id,)).fetchall()
    conn.close()
    return [dict(row) for row in candidates]

def check_existing_candidate(job_id, resume_name):
    # Reverted back to checking just the file name!
    conn = get_connection()
    res = conn.execute("SELECT id FROM candidates WHERE job_id = ? AND resume_name = ?", (job_id, resume_name)).fetchone()
    conn.close()
    return res if res else None

# ==========================================
# UTILITY QUERIES
# ==========================================

def get_all_users():
    conn = get_connection()
    users = conn.execute("SELECT id, email, role, created_at FROM users ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(row) for row in users]

def get_all_skills():
    return [
        "Python", "Java", "JavaScript", "React", "Django", "SQL", "AWS", 
        "Docker", "Kubernetes", "C++", "Spring Boot", "Machine Learning", 
        "Data Analysis", "Project Management", "Agile", "REST APIs"
    ]

def add_skill(skill_name):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO skills (skill_name) VALUES (?)", (skill_name,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False 
    finally:
        conn.close()

def delete_report(report_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))
    conn.commit()
    conn.close()

def delete_candidate(candidate_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
    conn.commit()
    conn.close()