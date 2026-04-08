import os
import time
import json
import re
from dotenv import load_dotenv
from groq import Groq

# Load the freshest API key
load_dotenv(override=True)

def setup_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY not found. Check your .env file.")
        return None
    return Groq(api_key=api_key)

def generate_custom_feedback(job_title, match_score, missing_skills, resume_text, jd_text):
    client = setup_groq_client()
    if not client: return "Generative AI is not configured."

    prompt = f"""
    You are a technical career coach. Give direct feedback to a candidate applying for '{job_title}'.
    RESUME:\n{resume_text}\n
    MISSING SKILLS: {missing_skills}\n
    TASK: Write a 3-sentence feedback paragraph. 
    1. First sentence MUST name a specific company/project from their resume. 
    2. Second sentence MUST connect existing experience to MISSING SKILLS.
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile", 
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Could not generate AI feedback at this time. (Error: {str(e)})"

def analyze_missing_skills(resume_text, jd_text):
    client = setup_groq_client()
    if not client: return "Generative AI is not configured."

    prompt = f"""
    Compare JD to Resume. JD:\n{jd_text}\nResume:\n{resume_text}
    Identify top 3-5 critical technical skills MISSING from the resume. Return ONLY a comma-separated list.
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content.replace('\n', '').strip()
    except Exception as e:
        return f"Error extracting skills: {str(e)}"

# ==========================================
# RESUME RESTRUCTURING LOGIC (NOW RETURNS JSON)
# ==========================================
def rewrite_resume(resume_text, missing_skills, job_title):
    client = setup_groq_client()
    if not client: return None

    prompt = f"""
    Rewrite the following resume for a '{job_title}' role. Format it professionally.
    RESUME:\n{resume_text}\n
    
    You MUST return the output strictly as a JSON object with the following exact keys. Do not add markdown codeblocks. Just the raw JSON.
    {{
        "name": "Candidate Full Name",
        "contact": "Email | Phone | LinkedIn",
        "summary": "Professional summary paragraph",
        "skills": "Bullet points of skills. Leave empty string if none.",
        "experience": "Bullet points of experience. Leave empty string if none.",
        "projects": "Bullet points of projects. Leave empty string if none.",
        "education": "Education details.",
        "certifications": "Certifications. Leave empty string if none."
    }}
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile", 
        )
        response_text = chat_completion.choices[0].message.content
        
        # Safely extract JSON even if AI adds formatting
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(response_text)
    except Exception as e:
        print("Error parsing JSON:", e)
        # Fallback structure
        return {"name": "Error Generating Resume", "contact": "", "summary": str(e), "skills": "", "experience": "", "projects": "", "education": "", "certifications": ""}