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
    """Get AI response based on user data and chat history."""
    try:
        client = OpenAI()

        # Get user data and chat history
        user_data = get_user_data(user_id)
        chat_history = get_chat_history(user_id, limit=10)  # Retrieve last 10 messages

        # Ensure we have user details
        if not user_data or 'name' not in user_data:
            raise ValueError("Could not retrieve user name from database")
        username = user_data['name']

        # Fetch user's historical data
        stress_logs = user_data.get("stress_logs", [])
        weight_logs = user_data.get("weight_logs", [])
        active_challenges = user_data.get("active_challenges", [])

        # Prepare structured historical data
        stress_history = "\n".join([f"- {log['date'].strftime('%Y-%m-%d')}: {log['stress_score']}/10" for log in stress_logs]) or "No stress logs recorded."
        weight_history = "\n".join([f"- {log['date'].strftime('%Y-%m-%d')}: {log['weight']} kg" for log in weight_logs]) or "No weight records found."
        challenges_summary = "\n".join(
            [f"- 🌟 **{ch['challenge_name']}** (Day {ch['progress']['current_day']})" for ch in active_challenges]
        ) or "No active challenges at the moment."

        # System message providing context
        system_message = {
            "role": "system",
            "content": f"""
You are a wellness assistant for {username}. You remember past conversations and provide helpful responses. 

### **Current User Metrics**
- 😌 **Stress Level:** {stress_logs[0]['stress_score'] if stress_logs else 'Not recorded'}
- 🏃‍♂️ **Activity Streak:** {len(user_data.get('activities', []))} days
- 📊 **BMI:** {user_data.get('assessments', [{}])[0].get('bmi', 'Not measured yet')}

### **Historical Data**
#### 🧘 **Stress Logs**
{stress_history}

#### ⚖️ **Weight History**
{weight_history}

#### 🎯 **Active Challenges**
{challenges_summary}

### **Chat Memory**
You remember the last 10 messages. Respond naturally and supportively.
"""
        }

        # Prepare chat messages (include user history)
        messages = [system_message]

        # Add recent chat history for context
        for db_role, content, _ in chat_history:
            role = "assistant" if db_role == "assistant" else "user"
            messages.append({"role": role, "content": content})

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Get AI response
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=200
        )

        # Extract assistant response
        ai_response = response.choices[0].message.content

        # Save conversation to database
        save_chat_message(user_id, "user", user_message)
        save_chat_message(user_id, "assistant", ai_response)

        return ai_response

    except Exception as e:
        return f"I apologize {username}, but I encountered an error: {str(e)}"