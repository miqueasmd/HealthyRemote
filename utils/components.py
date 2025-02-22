import streamlit as st
from typing import List, Dict
import openai
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
        # Get user data and recent chat history
        user_data = get_user_data(user_id)
        chat_history = get_chat_history(user_id)
        
        # Create system message with user context
        system_message = f"""You are a wellness assistant helping {user_data.get('name', 'there')}. 
        Their current stress score is {user_data.get('assessments', [{}])[0].get('stress_score', 'unknown') if user_data.get('assessments') else 'unknown'} 
        and their activity streak is {len(user_data.get('activities', []))} days.
        
        Provide personalized wellness advice based on their metrics and maintain a supportive, encouraging tone."""
        
        # Prepare messages for API
        messages = [
            {"role": "system", "content": system_message}
        ]
        
        # Add recent chat history (limit to last 5 messages for context)
        for role, content, _ in list(chat_history)[:5]:
            messages.append({"role": role, "content": content})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Get AI response
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        
        ai_response = response.choices[0].message.content
        
        # Save both messages to database
        save_chat_message(user_id, "user", user_message)
        save_chat_message(user_id, "assistant", ai_response)
        
        return ai_response
        
    except Exception as e:
        error_message = f"I apologize, but I encountered an error: {str(e)}"
        save_chat_message(user_id, "assistant", error_message)
        return error_message