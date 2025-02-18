import streamlit as st
from utils.components import init_spotify_player

init_spotify_player()

st.title("🧘‍♂️ Virtual Health Assistant")

st.markdown("""
Welcome to the Virtual Health Assistant! This assistant is designed to help you with personalized recommendations 
for preventing, diagnosing, and improving issues related to:

1. Muscular and joint pain.
2. Overweight.
3. Stress.

Please describe your issue or select a category to get started.
""")

# Add more content and functionality for the assistant here