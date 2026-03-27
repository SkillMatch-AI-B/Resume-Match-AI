from dotenv import load_dotenv
from google import genai
import os

# Load the variables from the .env file
load_dotenv()
# Put your real API key from Google AI Studio here
GEMINI_API_KEY = "AIzaSyCIbq8cmqH8RV5ZF21h5hyGb9WJ9Viw3Ac" 

def setup_gemini_client():
    # Retrieve the key from the environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: API Key not found. Check your .env file.")
        return None
    client = genai.Client(api_key=api_key)
    return client

def generate_custom_feedback(job_title, match_score, missing_skills):
    """
    Generates personalized, constructive feedback for the job seeker based on their score.
    """
    client = setup_gemini_client()
    if not client:
        return "Generative AI is not configured. Please add your API key."

    prompt = f"""
    You are an expert tech recruiter. A candidate applied for a '{job_title}' role.
    Their resume scored a {match_score}% match against the job description.
    They are missing the following key skills: {missing_skills}.
    
    Write a short, encouraging 3-sentence paragraph advising them on what to focus on learning next to improve their chances for this specific role. Do not use generic filler.
    """
    
    try:
        # Using the new SDK syntax and the fast flash model
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Could not generate AI feedback at this time. (Error: {str(e)})"

def generate_interview_questions(job_title, missing_skills):
    """
    Generates 3 technical interview questions targeting the candidate's weak points.
    """
    client = setup_gemini_client()
    if not client:
        return "Generative AI is not configured."

    if not missing_skills or missing_skills == "None! Perfect skill match.":
        return "Candidate has all required skills! Ask advanced architectural questions."

    prompt = f"""
    You are an expert interviewer hiring a '{job_title}'. 
    The candidate's resume did NOT mention these required skills: {missing_skills}.
    
    Generate exactly 3 technical interview questions to test if they actually know these missing skills, or to see how they would approach learning them. Keep the questions direct and professional. Number them 1, 2, 3.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Could not generate questions at this time. (Error: {str(e)})"
        
def analyze_missing_skills(resume_text, jd_text):
    """Uses Gemini to dynamically find missing skills without needing a manual database."""
    client = setup_gemini_client()
    if not client:
        return "Generative AI is not configured."

    prompt = f"""
    Act as an expert technical recruiter. 
    Compare this Job Description to this Candidate's Resume.
    
    Job Description:
    {jd_text}
    
    Candidate Resume:
    {resume_text}
    
    Identify the top 3 to 5 critical technical skills, tools, or requirements from the Job Description that are completely MISSING from the resume. 
    Return ONLY a comma-separated list of the missing skills. Do not write a paragraph. 
    If the candidate truly has everything, return "None! Perfect skill match."
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        # Strip out any weird formatting or newlines the AI might add
        return response.text.replace('\n', '').strip()
    except Exception as e:
        return f"Error extracting skills: {str(e)}"        