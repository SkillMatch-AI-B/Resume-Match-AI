import re
from sentence_transformers import SentenceTransformer, util
import database.db_queries as db

# Load the AI model once when the server starts (keeps the app fast!)
# all-MiniLM-L6-v2 is the industry standard for fast, accurate text similarity
model = SentenceTransformer('all-MiniLM-L6-v2')

def clean_text(text):
    """
    Cleans raw text by making it lowercase, removing special characters, 
    and stripping extra whitespace.
    """
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_skills(text, master_skills):
    """
    Scans the cleaned text for exact skill keywords from our database.
    """
    found_skills = []
    text_words = text.split()
    
    for skill in master_skills:
        if skill.lower() in text or skill.lower() in text_words:
            found_skills.append(skill)
            
    return list(set(found_skills))

def calculate_semantic_similarity(resume_text, jd_text):
    """
    Uses BERT (Sentence Transformers) to understand the underlying meaning 
    of the text, not just exact word matching.
    """
    if not resume_text or not jd_text:
        return 0.0
        
    # Convert texts into dense semantic vectors
    embeddings1 = model.encode(resume_text, convert_to_tensor=True)
    embeddings2 = model.encode(jd_text, convert_to_tensor=True)
    
    # Calculate the Cosine Similarity between the two semantic vectors
    cosine_score = util.cos_sim(embeddings1, embeddings2).item()
    
    # Ensure it doesn't drop below 0 and convert to percentage
    return round(max(cosine_score, 0.0) * 100, 2)

def analyze(resume_text, jd_text):
    """
    The master function: 80% Semantic BERT Score + 20% Keyword Skill Score.
    """
    clean_resume = clean_text(resume_text)
    clean_jd = clean_text(jd_text)
    
    master_skills = db.get_all_skills()
    if not master_skills:
        master_skills = ["Python", "Java", "SQL", "React", "AWS", "Machine Learning", "Excel"]
    
    # Extract hard skills
    resume_skills = extract_skills(clean_resume, master_skills)
    jd_skills = extract_skills(clean_jd, master_skills)
    missing_skills = list(set(jd_skills) - set(resume_skills))
    
    # 1. Get the advanced BERT context score
    context_score = calculate_semantic_similarity(clean_resume, clean_jd)
    
    # 2. Get the hard-skills keyword score
    if len(jd_skills) > 0:
        skill_score = (len(set(resume_skills).intersection(set(jd_skills))) / len(jd_skills)) * 100
    else:
        skill_score = 100.0
        
    # Apply 80/20 Weighting
    final_score = round((context_score * 0.8) + (skill_score * 0.2), 2)
    
    missing_str = ", ".join(missing_skills) if missing_skills else "None! Perfect skill match."
    found_str = ", ".join(resume_skills) if resume_skills else "No specific skills detected."
    
    return final_score, missing_str, found_str