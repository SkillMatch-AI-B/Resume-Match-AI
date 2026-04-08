import sys
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

import streamlit as st
import database.db_queries as db
import core.resume_parser as parser
import core.nlp_engine as matcher
import pandas as pd

# ==========================================
# SECURITY CHECK
# ==========================================
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("app.py")

if st.session_state.user_data['role'] != "Recruiter":
    st.error("Access Denied. You are not logged in as a Recruiter.")
    st.stop()

recruiter_id = st.session_state.user_data['id']

# ==========================================
# UI LAYOUT
# ==========================================
st.set_page_config(page_title="Recruiter Dashboard", page_icon="👔", layout="wide")
# --- SIDEBAR & LOGOUT ---
st.sidebar.success(f"Logged in as: {st.session_state.user_data['email']}")
if st.sidebar.button("Logout", type="primary"):
    st.session_state.clear() # Wipes the memory
    st.switch_page("app.py") # Kicks them back to the login screen
# ------------------------
st.title("👔 Recruiter Dashboard")
st.markdown("Manage job campaigns, bulk-process resumes, and find top talent using BERT AI.")

tab_jobs, tab_rank, tab_vault = st.tabs(["📝 1. Job Campaigns", "⚡ 2. Upload & Rank", "🗄️ 3. Candidate Vault"])

active_jobs = db.get_recruiter_jobs(recruiter_id)

# ------------------------------------------
# TAB 1: MANAGE JOB CAMPAIGNS
# ------------------------------------------
with tab_jobs:
    st.header("Create a New Job Campaign")
    with st.form("create_job_form", clear_on_submit=True):
        new_title = st.text_input("Job Title (e.g., Senior React Engineer)")
        new_jd = st.text_area("Job Description", height=150)
        if st.form_submit_button("Create Campaign", type="primary"):
            if new_title and new_jd:
                db.create_job(recruiter_id, new_title, new_jd)
                st.success(f"Campaign '{new_title}' created successfully!")
                st.rerun()
            else:
                st.warning("Please provide both a title and a description.")
                
    st.divider()
    st.subheader("Your Active Campaigns")
    if not active_jobs:
        st.info("You don't have any active job campaigns.")
    else:
        for job in active_jobs:
            st.markdown(f"**{job['title']}** (Created: {job['created_at'][:10]})")

# ------------------------------------------
# TAB 2: BULK UPLOAD & RANK (INTEGRATED WITH AI)
# ------------------------------------------
with tab_rank:
    st.header("Bulk Candidate Ranking")
    
    if not active_jobs:
        st.warning("Please create a Job Campaign first.")
    else:
        job_options = {f"{job['title']} ({job['created_at'][:10]})": (job['id'], job['description']) for job in active_jobs}
        selected_job_label = st.selectbox("1. Select the Job Campaign:", list(job_options.keys()))
        
        selected_job_id = job_options[selected_job_label][0]
        selected_jd_text = job_options[selected_job_label][1] # We need the JD text to compare against!
        
        uploaded_resumes = st.file_uploader("2. Upload Resumes (Bulk)", type=["pdf", "docx", "txt"], accept_multiple_files=True)
        
        if st.button("Process & Rank Candidates", type="primary", use_container_width=True):
            if uploaded_resumes:
                progress_bar = st.progress(0)
                status_text = st.empty()
                processed_count = 0
                skipped_count = 0  # Added counter for skipped duplicates
                
                for i, resume_file in enumerate(uploaded_resumes):
                    # FIX: DUPLICATE CHECK
                    # If candidate already exists in this specific campaign, skip them!
                    if db.check_existing_candidate(selected_job_id, resume_file.name):
                        skipped_count += 1
                        progress_bar.progress((i + 1) / len(uploaded_resumes))
                        continue
                    
                    status_text.text(f"🧠 AI is reading {resume_file.name}...")
                    
                    # 1. Parse the resume
                    resume_text = parser.parse_resume(resume_file)
                    
                    if not resume_text.startswith("Error:") and resume_text.strip():
                        # 2. Run the BERT NLP Engine!
                        match_score, missing, found_skills = matcher.analyze(resume_text, selected_jd_text)
                        
                        # 3. Save to database
                        db.add_candidate(selected_job_id, resume_file.name, match_score, found_skills)
                        processed_count += 1
                    else:
                        st.error(f"Could not read {resume_file.name}. Details: {resume_text[:50]}...")

                    progress_bar.progress((i + 1) / len(uploaded_resumes))
                
                status_text.text("Ranking complete!")
                
                # Show results summary including duplicates skipped
                if skipped_count > 0:
                    st.info(f"💡 Skipped {skipped_count} resume(s) that were already processed in this campaign.")
                if processed_count > 0:
                    st.success(f"Successfully processed {processed_count} new candidate(s). View results in the Vault.")
            else:
                st.warning("Please upload at least one resume.")

# ------------------------------------------
# TAB 3: CANDIDATE VAULT
# ------------------------------------------
with tab_vault:
    st.header("Candidate Vault")
    if not active_jobs:
        st.info("No campaigns available.")
    else:
        vault_job_options = {f"{job['title']} ({job['created_at'][:10]})": job['id'] for job in active_jobs}
        
        filter_job_label = st.selectbox("Filter by Campaign:", list(vault_job_options.keys()), key="vault_job_selector")
        filter_job_id = vault_job_options[filter_job_label]
        
        candidates = db.get_job_candidates(filter_job_id)
        
        if not candidates:
            st.info("No candidates processed for this campaign yet.")
        else:
            df = pd.DataFrame(candidates)[['resume_name', 'match_score', 'skills_found', 'uploaded_at']]
            df.columns = ["Candidate File", "Match Score (%)", "Skills Detected", "Date Processed"]
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.markdown("### 🗑️ Manage Candidates")
            
            # Map candidate names to their database IDs
            candidate_map = {c['resume_name']: c['id'] for c in candidates}
            
            col1, col2 = st.columns([3, 1])
            with col1:
                candidates_to_delete = st.multiselect("Select candidate(s) to remove from this campaign:", list(candidate_map.keys()))
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Remove Selected", type="secondary", use_container_width=True):
                    if candidates_to_delete:
                        for candidate_name in candidates_to_delete:
                            db.delete_candidate(candidate_map[candidate_name])
                        st.toast(f"Successfully removed {len(candidates_to_delete)} candidate(s).")
                        st.rerun()
                    else:
                        st.warning("Please select at least one candidate to remove.")