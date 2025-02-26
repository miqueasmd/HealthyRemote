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
    try:
        client = OpenAI()
        
        # Get comprehensive user data
        user_data = get_user_data(user_id)
        
        # Create system message with all available data
        system_message = {
            "role": "system",
            "content": f"""You are HealthyRemote, a wellness assistant for {user_data['name']}. 
You have access to their complete health records:

1. Weight History: {[f"{w['date'].strftime('%Y-%m-%d')}: {w['weight']}kg" for w in user_data['weight_logs']]}
2. Latest Assessment:
   - Stress Score: {user_data['assessments'][0]['stress_score'] if user_data['assessments'] else 'No data'}
   - BMI: {user_data['assessments'][0]['bmi'] if user_data['assessments'] else 'No data'}
3. Activity History: {len(user_data['activities'])} activities recorded
4. Stress History: {[f"{s['date'].strftime('%Y-%m-%d')}: {s['stress_score']}/10" for s in user_data['stress_logs']]}
5. Active Challenges: {[c['challenge_name'] for c in user_data['active_challenges']]}

You can access and reference this data when responding to queries.
Always provide accurate information based on these records.
When asked about your name, always respond that you are HealthyRemote."""
        }
        
        messages = [system_message]
        messages.append({"role": "user", "content": user_message})
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}"