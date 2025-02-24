import streamlit as st
from typing import List, Dict
from openai import OpenAI
from .database import save_chat_message, get_chat_history, get_user_data

def init_spotify_player():
    # Define music playlists
    MUSIC_PLAYLISTS = {
        "latin": "37i9dQZF1DX10zKzsJ2jva",
        "rock": "37i9dQZF1DWXRqgorJj26U",
        "pop": "37i9dQZF1DXcBWIGoYBM5M",
        "hip hop": "37i9dQZF1DX0XUsuxWHRQd",
        "relaxing": "37i9dQZF1DWZqd5JICZI0u"
    }

    # Create session state for music selection if it doesn't exist
    if 'music_genre' not in st.session_state:
        st.session_state.music_genre = "relaxing"

    # Add music controls to sidebar
    st.sidebar.markdown("### 🎵 Background Music")
    selected_genre = st.sidebar.selectbox(
        "Choose music genre:",
        list(MUSIC_PLAYLISTS.keys()),
        format_func=lambda x: x.title(),
        key="music_genre_selector"
    )

    # Update session state if genre changed
    if selected_genre != st.session_state.music_genre:
        st.session_state.music_genre = selected_genre

    # Display Spotify player
    st.sidebar.markdown(f"""
        <iframe style="border-radius:12px" 
        src="https://open.spotify.com/embed/playlist/{MUSIC_PLAYLISTS[st.session_state.music_genre]}?utm_source=generator" 
        width="100%" 
        height="152" 
        frameBorder="0" 
        allowfullscreen="" 
        allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
        loading="lazy">
        </iframe>
    """, unsafe_allow_html=True)

def get_ai_response(user_id: int, user_message: str) -> str:
    """Get AI response based on user data and chat history"""
    try:
        client = OpenAI()
        
        # Get user data and recent chat history
        user_data = get_user_data(user_id)
        chat_history = get_chat_history(user_id)
        
        # Get username from user_data, fail if not found
        if not user_data or 'name' not in user_data:
            raise ValueError("Could not retrieve user name from database")
            
        username = user_data['name']  # No default value - we want the actual name
        
        # Create system message with user context
        system_message = {
            "role": "system",
            "content": f"""You are a wellness assistant for {username}. 
CRITICAL INSTRUCTIONS:
1. The user's name is '{username}' - ALWAYS use this name
2. If asked about their name, respond with: "Yes, I know you're {username}!"
3. Use their name naturally in responses
4. Keep track of their metrics:
   - Stress Score: {user_data.get('assessments', [{}])[0].get('stress_score', 'Not measured yet')}
   - Activity Streak: {len(user_data.get('activities', []))} days
   - BMI: {user_data.get('assessments', [{}])[0].get('bmi', 'Not measured yet')}
5. Reference these metrics when relevant
6. Maintain a supportive and personalized tone"""
        }
        
        # Prepare messages for API
        messages = [system_message]
        
        # Add recent chat history (last 5 messages)
        for db_role, content, _ in list(chat_history)[-5:]:
            role = "assistant" if db_role == "assistant" else "user"
            messages.append({"role": role, "content": content})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Get AI response
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"I apologize {username}, but I encountered an error: {str(e)}"