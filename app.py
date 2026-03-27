import streamlit as st
import core.auth as auth
import time
import database.db_setup as db_setup
# Force the database to build its tables if they are missing!
db_setup.create_database()

# Configure the main page settings
st.set_page_config(page_title="SkillMatch AI", page_icon="🎯", layout="centered")

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
# This keeps track of whether the user is logged in across page refreshes
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_data" not in st.session_state:
    st.session_state.user_data = None

# ==========================================
# ROUTING LOGIC (If logged in)
# ==========================================
if st.session_state.logged_in:
    role = st.session_state.user_data['role']
    
    # We put a logout button in the sidebar so it's accessible from any page
    st.sidebar.success(f"Logged in as: {st.session_state.user_data['email']}")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    # Automatically redirect the user to their specific dashboard based on their role
    try:
        if role == "Job Seeker":
            st.switch_page("pages/1_JobSeeker.py")
        elif role == "Recruiter":
            st.switch_page("pages/2_Recruiter.py")
    except FileNotFoundError:
        st.warning("Redirecting... (If you see this, the 'pages' folder files aren't created yet!)")
        st.stop()

# ==========================================
# AUTHENTICATION UI (If NOT logged in)
# ==========================================
st.title("🎯 SkillMatch AI")
st.subheader("Smart Resume Analysis & Recruitment Platform")
st.markdown("Welcome! Please log in or create an account to continue.")

# Create two tabs for a cleaner UI
tab1, tab2 = st.tabs(["Login", "Register"])

with tab1:
    st.header("Login")
    login_email = st.text_input("Email", key="login_email")
    login_password = st.text_input("Password", type="password", key="login_pass")
    
    if st.button("Login", type="primary", use_container_width=True):
        if login_email and login_password:
            # Check credentials against the database
            user = auth.authenticate_user(login_email, login_password)
            if user:
                st.success("Login successful! Redirecting to your dashboard...")
                st.session_state.logged_in = True
                st.session_state.user_data = user
                time.sleep(1)  # Brief pause so the user sees the success message
                st.rerun()     # This refreshes the app and triggers the routing logic above
            else:
                st.error("Invalid email or password.")
        else:
            st.warning("Please enter both email and password.")

with tab2:
    st.header("Create an Account")
    reg_email = st.text_input("Email", key="reg_email")
    reg_password = st.text_input("Password", type="password", key="reg_pass")
    
    # This dropdown solves your Point #1: It automatically assigns the correct role on signup
    reg_role = st.selectbox("I am a:", ["Job Seeker", "Recruiter"])
    
    if st.button("Register", use_container_width=True):
        if reg_email and len(reg_password) >= 6:
            success = auth.register_user(reg_email, reg_password, reg_role)
            if success:
                st.success(f"Account created successfully as a {reg_role}! Please go to the Login tab.")
            else:
                st.error("This email is already registered. Please try logging in.")
        else:
            st.warning("Please provide a valid email and a password (minimum 6 characters).")