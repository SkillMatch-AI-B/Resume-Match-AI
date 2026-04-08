from fpdf import FPDF
import re

def generate_pdf_bytes(job_title, match_score, missing_skills, ai_feedback):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Resume Analysis Report: {job_title}", ln=True, align='C')
    pdf.ln(5)
    
    # Match Score
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Match Score: {match_score}%", ln=True)
    pdf.ln(5)
    
    # Missing Skills
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(220, 53, 69) # Red color for missing skills
    pdf.cell(0, 10, "Critical Missing Skills:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 6, str(missing_skills).encode('latin-1', 'replace').decode('latin-1'))
    pdf.ln(5)
    
    # AI Feedback
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 102, 204) # Blue color for AI Coach
    pdf.cell(0, 10, "AI Coach Insights:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(0, 0, 0)
    
    # Clean up markdown bolding for the PDF
    clean_feedback = ai_feedback.replace('**', '')
    pdf.multi_cell(0, 6, clean_feedback.encode('latin-1', 'replace').decode('latin-1'))
    
    # BULLETPROOF PDF OUTPUT FIX
    try:
        # For fpdf2
        return bytes(pdf.output())
    except Exception:
        # For older fpdf versions
        return pdf.output(dest='S').encode('latin-1', 'replace')