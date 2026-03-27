import sys
import os

# --- BULLETPROOF IMPORT FIX ---
# Force Python to recognize the main project directory
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)
# ------------------------------

import streamlit as st
import database.db_queries as db
import core.resume_parser as parser
import core.nlp_engine as matcher
import core.llm_helper as llm
import utils.report_generator as rg
import core.llm_helper as llm_helper

# ... [The rest of your code stays exactly the same below this] ...

# ==========================================
# SECURITY CHECK
# ==========================================
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("app.py")

if st.session_state.user_data['role'] != "Job Seeker":
    st.error("Access Denied. You are not logged in as a Job Seeker.")
    st.stop()

user_id = st.session_state.user_data['id']

# ==========================================
# UI LAYOUT
# ==========================================
st.set_page_config(page_title="Job Seeker Dashboard", page_icon="📄", layout="wide")
# --- SIDEBAR & LOGOUT ---
st.sidebar.success(f"Logged in as: {st.session_state.user_data['email']}")
if st.sidebar.button("Logout", type="primary"):
    st.session_state.clear() # Wipes the memory
    st.switch_page("app.py") # Kicks them back to the login screen
# ------------------------
st.title("📄 Job Seeker Dashboard")
st.markdown("Analyze your resume against job descriptions using Semantic AI.")

tab_analyze, tab_history = st.tabs(["🔍 New Analysis", "📚 My Reports"])

# ------------------------------------------
# TAB 1: NEW ANALYSIS
# ------------------------------------------
with tab_analyze:
    st.header("Analyze a New Job")
    
    col1, col2 = st.columns(2)
    with col1:
        job_title_input = st.text_input("Job Title (e.g., Python Developer)")
        st.markdown("### Step 1: Provide Your Resume")
        
        # Create a toggle so the user can choose how to give you their resume
        upload_method = st.radio("Choose input method:", ["📁 Upload File (PDF/DOCX)", "📝 Paste Text Manually"], horizontal=True)
        
        resume_text = "" # Create an empty variable to hold the text
        resume_file = None 
        if upload_method == "📁 Upload File (PDF/DOCX)":
            # FIXED: Added the unique key right here at the end of this line!
            resume_file = st.file_uploader("Upload your latest Resume", type=["pdf", "docx", "txt"], key="resume_uploader_main")
            
            if resume_file:
                # Use our heavy-duty parser
                parsed_result = parser.parse_resume(resume_file)
                
                # Check if our parser threw one of our custom error messages
                if parsed_result.startswith("Error:"):
                    st.error(f"Could not read this file. Please try the '📝 Paste Text Manually' option above. ({parsed_result})")
                else:
                    resume_text = parsed_result
                    st.success("Resume read successfully!")
                    
        else:
            # The Fallback Option!
            resume_text = st.text_area("Paste your full resume text here:", height=250)
            if resume_text:
                st.success("Resume text accepted!")
    with col2:
        jd_text = st.text_area("Paste the Job Description here:", height=200)

    if st.button("Analyze & Save Report", type="primary", use_container_width=True):
        # st.info(f"DEBUG X-RAY -> Title: {'✅' if job_title else '❌'} | Resume: {'✅' if resume_text else '❌'} | JD: {'✅' if jd_text else '❌'}")
        if resume_text and jd_text and job_title_input:
            with st.spinner("🧠 AI is reading and comparing your resume using BERT..."):
                
                
                # Check if the parser failed (e.g., corrupted file)
                if "Error" in resume_text or not resume_text.strip():
                    st.error(f"Failed to read the resume. {resume_text}")
                else:
                    # 2. Run the Real AI NLP Engine!
                    # 1. Run your BERT engine to calculate the match_score and found_skills
                    match_score, _, found_skills = matcher.analyze(resume_text, jd_text)
                    
                    # 2. Let the Gemini AI dynamically read the JD to find the true missing skills!
                    missing_skills = llm_helper.analyze_missing_skills(resume_text, jd_text)
                    
                    # 3. Generate REAL custom feedback using Gemini AI!
                    st.text("✨ Generating personalized AI feedback...")
                    ai_feedback = llm.generate_custom_feedback(job_title_input, match_score, missing_skills)
                    
                    # 4. Save the results to the SQLite Database
                    db.save_report(
                        user_id=user_id,
                        job_title=job_title_input,
                        match_score=match_score,
                        missing_skills=missing_skills,
                        ai_feedback=ai_feedback
                    )
                    
                    st.success(f"Analysis Complete! You scored an **{match_score}%** semantic match.")
                    st.info("Your full report has been saved to the 'My Reports' tab.")
        else:
            st.warning("Please provide a Job Title, provide a Resume, and paste a Job Description.")

# ------------------------------------------
# TAB 2: MY REPORTS (HISTORY)
# ------------------------------------------
with tab_history:
    st.header("Your Past Analyses")
    
    reports = db.get_user_reports(user_id)
    
    if not reports:
        st.info("You haven't analyzed any jobs yet.")
    else:
        for report in reports:
            # Color code the score
            score = report['match_score']
            if score >= 80:
                score_color = "🟢"
            elif score >= 50:
                score_color = "🟡"
            else:
                score_color = "🔴"

            with st.expander(f"{score_color} {report['job_title']} — {score}% Match (Saved: {report['created_at'][:10]})"):
                st.markdown(f"**Missing Skills:** {report['missing_skills']}")
                st.markdown("---")
                st.markdown("**AI Insights:**")
                st.write(report['ai_feedback'])
                
                # Create the PDF directly from the database record
                pdf_bytes = rg.generate_pdf_bytes(
                    job_title=report['job_title'], 
                    match_score=report['match_score'], 
                    missing_skills=report['missing_skills'], 
                    ai_feedback=report['ai_feedback']
                )
                
                # Streamlit Download Button
                # Place buttons side-by-side
                btn_col1, btn_col2 = st.columns(2)
                
                with btn_col1:
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"{report['job_title'].replace(' ', '_')}_Report.pdf",
                        mime="application/pdf",
                        key=f"download_{report['id']}"
                    )
                
                with btn_col2:
                    if st.button("🗑️ Delete Report", key=f"delete_{report['id']}", type="secondary"):
                        db.delete_report(report['id'])
                        st.toast("Report deleted successfully!")
                        st.rerun() # Instantly refreshes the page to hide the deleted report
