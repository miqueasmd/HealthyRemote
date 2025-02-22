from dotenv import load_dotenv
load_dotenv()  # This must be before any other imports
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.database import init_db, get_or_create_user, get_user_data, get_user_by_email, create_new_user, save_chat_message, get_chat_history
from utils.components import init_spotify_player, get_ai_response  # Added get_ai_response here

# Page configuration
st.set_page_config(
    page_title="Healthy Remote Wellness Platform",
    page_icon="🧘‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_spotify_player()

# Initialize database
init_db()

# Session state initialization
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

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
                st.session_state.user_id = user_id
                st.session_state.authenticated = True
                st.rerun()
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
                        st.session_state.authenticated = True
                        st.success("Account created successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating account: {e}")
                else:
                    st.warning("Please fill in all fields")

else:
    # Main page layout for authenticated users
    st.title("🧘‍♂️ Healthy Remote Wellness Platform")

    # Welcome message
    st.markdown("""
    Welcome to your personal wellness companion! This platform is designed to help remote workers 
    like you maintain and improve their physical and mental well-being.

    ### What we offer:
    1. 📋 **Wellness Assessments** - Track your stress levels and physical health
    2. 📈 **Progress Tracking** - Monitor your wellness journey
    3. 📚 **Educational Resources** - Learn about maintaining a healthy remote work lifestyle
    4. 🧘‍♂️ **Virtual Health Assistant** - Get personalized recommendations for your well-being
    
    Get started by navigating to the Assessment section in the sidebar!
    """)

    # Logout button in sidebar
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.rerun()

    # Quick status overview using database queries
    try:
        user_data = get_user_data(st.session_state.user_id)
        if user_data['assessments']:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    label="Latest Stress Score",
                    value=f"{user_data['assessments'][-1].get('stress_score', 0)}/10"
                )
            with col2:
                st.metric(
                    label="Activity Streak",
                    value=f"{len(user_data['activities'])} days"
                )
            with col3:
                st.metric(
                    label="Latest BMI",
                    value=f"{user_data['assessments'][-1].get('bmi', 0):.1f}"
                )
        else:
            st.info("👈 Start by taking your first assessment in the Assessment section!")
    except Exception as e:
        st.error(f"Error fetching user data: {e}")

    # Chat Interface
    st.header("💬 Chat with Your Wellness Assistant")

    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Load chat history from database
        chat_history = get_chat_history(st.session_state.user_id)
        for role, content, _ in reversed(chat_history):  # Reverse to show oldest first
            st.session_state.messages.append({"role": role, "content": content})
        
        # If no history, create initial greeting
        if not chat_history:
            user_data = get_user_data(st.session_state.user_id)
            initial_greeting = f"Hello {user_data.get('name', 'there')}! How can I help you with your wellness journey today?"
            st.session_state.messages.append({"role": "assistant", "content": initial_greeting})
            save_chat_message(st.session_state.user_id, "assistant", initial_greeting)

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("How can I help you today?"):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        save_chat_message(st.session_state.user_id, "user", prompt)

        # Get and display assistant response
        with st.chat_message("assistant"):
            response = get_ai_response(st.session_state.user_id, prompt)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        save_chat_message(st.session_state.user_id, "assistant", response)

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>Remember to take regular breaks and stay active! 💪</p>
        </div>
        """,
        unsafe_allow_html=True
    )