import streamlit as st
import openai
import os
from utils.components import init_spotify_player
from .database import get_user_by_email, get_user_data, save_chat_message, get_chat_history

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

def get_ai_response(user_id: int, user_message: str) -> str:
    """Get AI response with personalized user context"""
    try:
        # Get user data including name and latest metrics
        user_data = get_user_data(user_id)
        
        # Get user's latest assessment
        latest_assessment = user_data['assessments'][0] if user_data['assessments'] else None
        
        # Create personalized system message
        system_message = {
            "role": "system",
            "content": f"""You are a wellness assistant helping {user_data.get('name', 'there')}. 
            Current metrics:
            - Stress Score: {latest_assessment.get('stress_score', 'unknown') if latest_assessment else 'unknown'}
            - Activity Streak: {len(user_data['activities'])} days
            - Latest BMI: {latest_assessment.get('bmi', 'unknown') if latest_assessment else 'unknown'}
            
            Provide personalized wellness advice using their name and metrics."""
        }
        
        # Get recent chat history
        chat_history = get_chat_history(user_id, limit=5)
        messages = [system_message]
        
        # Add chat history to context
        for role, content, _ in chat_history:
            messages.append({"role": role, "content": content})
            
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Get OpenAI response
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        
        ai_response = response.choices[0].message.content
        
        # Save the conversation
        save_chat_message(user_id, "user", user_message)
        save_chat_message(user_id, "assistant", ai_response)
        
        return ai_response
        
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}"

# User input
user_input = st.text_area("Describe your issue or ask a question:")

if st.button("Get Recommendation"):
    if user_input:
        try:
            user_id = get_user_by_email(st.session_state['email'])['id']
            recommendation = get_ai_response(user_id, user_input)
            st.markdown(f"**Recommendation:** {recommendation}")

        except Exception as e:
            st.error(f"Error generating recommendation: {e}")

    else:
        st.warning("Please enter a description or question.")