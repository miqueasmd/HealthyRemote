import streamlit as st
import openai
import os
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

# Load OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# User input
user_input = st.text_area("Describe your issue or ask a question:")

if st.button("Get Recommendation"):
    if user_input:
        try:
            # Updated API call for openai>=1.0.0
            client = openai.Client()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_input},
                ],
                max_tokens=150,
                temperature=0.7,
            )

            recommendation = response.choices[0].message.content.strip()
            st.markdown(f"**Recommendation:** {recommendation}")

        except Exception as e:
            st.error(f"Error generating recommendation: {e}")

    else:
        st.warning("Please enter a description or question.")