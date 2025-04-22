from dotenv import load_dotenv
load_dotenv()  # This must be before any other imports
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.database import init_db, get_or_create_user, get_user_data, get_user_by_email, create_new_user, save_chat_message, get_chat_history
from utils.components import init_spotify_player, interpret_bmi, get_ai_response  # Added get_ai_response here

# Page configuration
st.set_page_config(
    page_title="Healthy Remote Wellness Platform",
    page_icon="🧘‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_spotify_player()

# Add creator credits below Spotify player with link
st.sidebar.markdown("---")  # Add a divider
st.sidebar.markdown("<div style='text-align: center; color: #555;'><small>Created by: <b>MMD</b><br><a href='https://miqueasmd.github.io/' target='_blank'>Miqueas Molina Delgado</a></small></div>", unsafe_allow_html=True)

# Initialize database
init_db()

# Session state initialization
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'email' not in st.session_state:
    st.session_state.email = None
if 'username' not in st.session_state:  # Add username initialization
    st.session_state.username = None

# Login/Signup System
if not st.session_state.authenticated:
    st.title("🧘‍♂️ Healthy Remote Wellness Platform")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:  # Login
        st.header("Login")
        login_email = st.text_input("Email", key="login_email")
        if st.button("Login"):
            user_id = get_user_by_email(login_email)
            if user_id:
                try:
                    user_data = get_user_data(user_id)
                    if not user_data or 'name' not in user_data:
                        st.error("Could not retrieve user data")
                        st.stop()
                    
                    st.session_state.user_id = user_id
                    st.session_state.email = login_email
                    st.session_state.username = user_data['name']
                    st.session_state.authenticated = True
                    st.session_state.chat_history = user_data.get('chat_history', [])
                    st.rerun()
                except Exception as e:
                    st.error(f"Error during login: {str(e)}")
            else:
                st.error("User not found. Please sign up if you're new!")

    with tab2:  # Sign Up
        st.header("Sign Up")
        with st.form("signup_form"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            submitted = st.form_submit_button("Sign Up")

            if submitted:
                if name and email:
                    try:
                        user_id = create_new_user(name, email)
                        st.session_state.user_id = user_id
                        st.session_state.email = email
                        st.session_state.username = name  # Store name in session
                        st.session_state.authenticated = True
                        st.success(f"Account created successfully, {name}!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating account: {e}")
                else:
                    st.warning("Please fill in all fields")

else:
    # Main page layout for authenticated users
    st.title("🧘‍♂️ Healthy Remote Wellness Platform")

    # Welcome message
    st.markdown(f"""
    Welcome to your personal wellness companion, {st.session_state.username}! <br><br>
    This platform is designed to help remote workers like you maintain and improve their physical and mental well-being.

    ### What we offer:
    1. 📋 **Wellness Assessments** - Track your stress levels and physical health
    2. 📈 **Progress Tracking** - Monitor your wellness journey
    3. 📚 **Educational Resources** - Learn about maintaining a healthy remote work lifestyle
    4. 🧘‍♂️ **Virtual Health Assistant** - Get personalized recommendations for your well-being
    
    Get started by navigating to the Assessment section in the sidebar!
    """, unsafe_allow_html=True)

    # Logout button in sidebar
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.email = None
        st.session_state.username = None  # Clear username on logout
        st.rerun()

    # Quick status overview using database queries
    try:
        user_data = get_user_data(st.session_state.user_id)
        if user_data['assessments']:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    label="Latest Stress Score",
                    value=f"{user_data['assessments'][0].get('stress_score', 0)}/10"
                )
            with col2:
                st.metric(
                    label="Activity Streak",
                    value=f"{len(user_data['activities'])} days"
                )
            with col3:
                bmi_value = user_data['assessments'][0].get('bmi', 0)
                bmi_category = interpret_bmi(bmi_value)
                st.metric(
                    label="Latest BMI",
                    value=f"{bmi_value:.1f}",
                    help=f"Ask the assistant or print the PDF Report (Progress section) to know more about your BMI"
                )
                st.caption(f"{bmi_category}")
        else:
            st.info("👈 Start by taking your first assessment in the Assessment section!")
    except Exception as e:
        st.error(f"Error fetching user data: {e}")
