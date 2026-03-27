from fpdf import FPDF
import datetime

def sanitize_text(text):
    """
    Cleans up fancy AI typography (smart quotes, dashes) into standard 
    keyboard characters so the PDF generator doesn't crash.
    """
    if not text:
        return ""
    
    # Dictionary of fancy Unicode characters and their basic ASCII equivalents
    replacements = {
        '\u2013': '-',   # en dash
        '\u2014': '--',  # em dash
        '\u2018': "'",   # left single quote
        '\u2019': "'",   # right single quote
        '\u201c': '"',   # left double quote
        '\u201d': '"',   # right double quote
        '\u2026': '...', # ellipsis
        '\u2022': '*'    # bullet point
    }
    
    for original, new in replacements.items():
        text = text.replace(original, new)
        
    # As a final safety net, strip any remaining emojis or weird symbols
    return text.encode('latin-1', 'ignore').decode('latin-1')


def generate_pdf_bytes(job_title, match_score, missing_skills, ai_feedback):
    """
    Creates a beautifully formatted PDF report in-memory and returns it as bytes.
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Sanitize all inputs before putting them in the PDF
    safe_title = sanitize_text(job_title)
    safe_missing = sanitize_text(missing_skills)
    safe_feedback = sanitize_text(ai_feedback)
    
    # Title
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(41, 128, 185)
    pdf.cell(0, 15, txt="SkillMatch AI - Analysis Report", ln=True, align='C')
    
    # Date & Job Title
    pdf.set_font("Arial", 'I', 12)
    pdf.set_text_color(100, 100, 100)
    date_str = datetime.datetime.now().strftime("%B %d, %Y")
    pdf.cell(0, 10, txt=f"Generated on: {date_str} | Target Role: {safe_title}", ln=True, align='C')
    pdf.ln(10)
    
    # Match Score
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, txt=f"Overall Match Score: {match_score}%", ln=True)
    pdf.ln(5)
    
    # Missing Skills
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt="Identified Skill Gaps:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 8, txt=safe_missing)
    pdf.ln(5)
    
    # AI Feedback
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt="AI Recruiter Insights:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 8, txt=safe_feedback)
    
    # Output the PDF as a byte string for Streamlit
    return bytes(pdf.output(dest='S'), 'latin1')