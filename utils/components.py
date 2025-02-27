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

def get_ai_response(user_id: int, user_message: str, previous_response: str = "") -> str:
    try:
        client = OpenAI()
        
        # Get comprehensive user data
        user_data = get_user_data(user_id)

        # Create conversation context from chat history
        conversation_history = user_data.get('chat_history', [])
        # Take only the last 15 messages to avoid token limits
        recent_history = conversation_history[-15:] if len(conversation_history) > 15 else conversation_history
        conversation_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_history])

        # Include previous response if available
        if previous_response:
            conversation_context += f"\nAssistant: {previous_response}"

        # Create a formatted string for all assessments
        assessments_info = "\n".join([
            f"- Date: {assessment['date']}, Stress Score: {assessment['stress_score']}, BMI: {assessment['bmi']}"
            for assessment in user_data['assessments']
        ])
        
        # Track if we recently told a story
        recently_told_story = False
        latest_story = None
        
        # Get the last 3 exchanges to check for a recent story
        for i, msg in enumerate(reversed(recent_history)):
            if i >= 6:  # Look at last 3 exchanges (user+assistant)
                break
                
            if msg['role'] == 'assistant':
                if "This concludes the story" in msg['content'] or "Would you like to see more" in msg['content']:
                    recently_told_story = True
                    latest_story = msg['content']
                    break
        
        # Check if user is asking about story ending
        is_asking_about_ending = any(phrase in user_message.lower() for phrase in 
            ["end of story", "story end", "finished", "is that the end", "is that all", "is it over", "that was short"])
            
        # Check if user is asking about "my story" or "my health story"
        is_asking_about_user_story = any(phrase in user_message.lower() for phrase in 
            ["my story", "my health story", "my journey", "my health journey", "my data story"])
        
        # Add more context to system message
        system_content = f"""You are HealthyRemote, a wellness assistant for {user_data['name']}. 
You have access to their complete health records, previous conversation context, and previous assessments:

1. Weight History: {[f"{w['date'].strftime('%Y-%m-%d')}: {w['weight']}kg" for w in user_data['weight_logs']]}
2. Latest Assessment:
   - Stress Score: {user_data['assessments'][0]['stress_score'] if user_data['assessments'] else 'No data'}
   - BMI: {user_data['assessments'][0]['bmi'] if user_data['assessments'] else 'No data'}
3. Activity History: {len(user_data['activities'])} activities recorded
4. Stress History: {[f"{s['date'].strftime('%Y-%m-%d')}: {s['stress_score']}/10" for s in user_data['stress_logs']]}
5. Active Challenges: {[c['challenge_name'] for c in user_data['active_challenges']]}

Important formatting instructions:
- Keep paragraphs short (2-4 sentences max)
- Add line breaks between paragraphs
- When telling stories, use shorter paragraphs similar to a novel
- When asked to "continue" a story, always reference what happened in the previous response
- When asked if a story is complete or ended, confirm clearly whether it's the end or not
- Always add a clear ending sentence like "This concludes the story" when finishing a story
- When providing user data or health information, always format it clearly with headers and line breaks
- Remember that when the user says "continue", they want you to continue what you were just talking about"""

        # If we recently told a story, add reminder about it
        if recently_told_story:
            system_content += "\n\nYou recently told a story that concluded or paused. If the user asks about 'the story', they are referring to this recent narrative."
            
        # Add reminder about health stories
        system_content += "\n\nWhen talking about 'my story' or 'my health journey', the user is referring to a narrative about their health data and progress. Treat these as stories too."
            
        system_message = {
            "role": "system",
            "content": system_content
        }
        
        messages = [system_message]
        
        # Find last story in conversation history
        last_story = None
        for msg in reversed(conversation_history):
            if msg['role'] == 'assistant' and any(phrase in msg['content'].lower() for phrase in 
                ["once upon a time", "there lived", "story", "journey", "adventure", "this concludes the story"]):
                last_story = msg['content']
                break
        
        # Handle specific types of messages
        if is_asking_about_ending and is_asking_about_user_story:
            # They're asking about their health story/journey
            messages.append({"role": "system", "content": "The user is asking about their health story you just shared. Confirm whether it's complete and summarize the key points of their health journey."})
            messages.append({"role": "assistant", "content": previous_response})
            messages.append({"role": "user", "content": user_message})
            
        elif is_asking_about_ending:
            # For general story ending questions
            if "This concludes the story" in previous_response:
                messages.append({"role": "system", "content": "The story has concluded. Confirm this to the user and briefly reflect on the story's message."})
            elif "Would you like to see more" in previous_response:
                messages.append({"role": "system", "content": "The story is NOT complete. Tell the user they can type 'continue' to see more."})
            else:
                # Look for the most recent story conclusion in history
                for msg in reversed(conversation_history):
                    if msg['role'] == 'assistant' and "This concludes the story" in msg['content']:
                        messages.append({"role": "system", "content": "The user is asking about a story you previously completed. Confirm that it was concluded."})
                        break
            
            messages.append({"role": "assistant", "content": previous_response})
            messages.append({"role": "user", "content": user_message})
            
        elif user_message.lower() == "continue" and previous_response:
            # Get last response and tell the API to continue from there
            messages.append({"role": "assistant", "content": previous_response})
            messages.append({"role": "user", "content": "Please continue from where you left off. Keep paragraphs short (2-3 sentences)."})
            
        elif user_message.lower() == "continue" and last_story and not previous_response:
            # If no previous response but we have a story in history, use that
            messages.append({"role": "assistant", "content": last_story})
            messages.append({"role": "user", "content": "Please continue the story from where you left off. Keep paragraphs short (2-3 sentences)."})
            
        elif user_message == "Please continue but keep it concise and finish the story in this response." and previous_response:
            messages.append({"role": "assistant", "content": previous_response})
            messages.append({"role": "user", "content": "Please continue and conclude the story. Keep paragraphs short (2-3 sentences) and make sure to provide a satisfying ending. End with 'This concludes the story.'"})
            
        else:
            # Check if this is a request for a story
            is_story_request = any(phrase in user_message.lower() for phrase in 
                ["tell me a story", "tell a story", "share a story", "story about", "make up a story", "long story"])
            
            # Check if this is a request for user data or health story
            is_data_request = any(phrase in user_message.lower() for phrase in
                ["my data", "my information", "my records", "my history", "my assessments", "my logs", 
                 "info about me", "tell me about me", "everything about me", "all the info", "all my data"])
                 
            is_health_story_request = any(phrase in user_message.lower() for phrase in
                ["my story", "tell me my story", "my health story", "my health journey", "based on my records", 
                 "story of my health", "narrative about me", "health narrative", "know about me"])
            
            if is_story_request:
                # Add specific instruction for story endings
                messages.append({"role": "user", "content": user_message})
                messages.append({"role": "system", "content": "Tell an engaging story with a clear beginning, middle, and end. When you complete the final part of a story, always clearly state 'This concludes the story.' at the end."})
            elif is_data_request:
                messages.append({"role": "user", "content": user_message})
                messages.append({"role": "system", "content": "Provide the user's data in a clear, organized format with headers and bullet points. Include all relevant information from their health records."})
            elif is_health_story_request:
                messages.append({"role": "user", "content": user_message})
                messages.append({"role": "system", "content": "Create a narrative about the user's health journey based on their data. Make it personal and engaging. When you complete the story, clearly state 'This concludes the story.' at the end."})
            else:
                messages.append({"role": "user", "content": user_message})
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )
        
        response_text = response.choices[0].message.content
        
        # Fix for duplicate "Would you like to see" text
        response_text = response_text.replace("Would you like to see.\n\n", "")
        response_text = response_text.replace("Would you like to see.\n", "")
        response_text = response_text.replace("Would you like to see.", "")
        
        # Improve paragraph formatting by breaking up long paragraphs
        sentences = response_text.split('. ')
        formatted_paragraphs = []
        current_paragraph = []
        
        for sentence in sentences:
            if not sentence.strip():
                continue
                
            current_paragraph.append(sentence)
            
            # After 2-3 sentences or if the sentence ends with a quotation mark, create a new paragraph
            if len(current_paragraph) >= 2 or sentence.endswith('"') or sentence.endswith("'"):
                formatted_paragraphs.append('. '.join(current_paragraph) + ('.' if not current_paragraph[-1].endswith('.') else ''))
                current_paragraph = []
        
        # Add any remaining sentences as a final paragraph
        if current_paragraph:
            formatted_paragraphs.append('. '.join(current_paragraph) + ('.' if not current_paragraph[-1].endswith('.') else ''))
        
        # Join paragraphs with double newlines
        formatted_response = '\n\n'.join(formatted_paragraphs)
        
        # Fix for duplicate "Would you like to see" text
        formatted_response = formatted_response.replace("Would you like to see.\n\n", "")
        formatted_response = formatted_response.replace("Would you like to see.\n", "")
        formatted_response = formatted_response.replace("Would you like to see.", "")
        
        # Determine if continuation prompt should be added
        is_story_response = any(phrase in formatted_response.lower() for phrase in 
            ["once upon a time", "there lived", "story", "journey", "adventure"]) or "concludes the story" in formatted_response.lower()
            
        # Also consider health narratives as stories
        is_health_narrative = any(phrase in user_message.lower() for phrase in 
            ["my story", "health story", "journey", "narrative"]) or any(name in formatted_response.lower() for name in ["paco", "elara"])
            
        # Detect if this is likely a data response
        is_data_response = any(term in user_message.lower() for term in
            ["records", "assessments", "logs", "data", "weight", "stress", "activities", 
             "info", "everything", "about me", "know about me", "information"])
        
        # Check if the response contains significant amounts of user data
        contains_user_data = any(term in formatted_response.lower() for term in
            ["bmi", "stress score", "stress level", "weight", "kg", "assessment", "challenge"])
        
        # Add continuation prompt for long responses that aren't answers to "is it finished" questions
        response_word_count = len(formatted_response.split())
        should_add_prompt = (
            # Not asking if the story is over
            not is_asking_about_ending and 
            
            # Not already finishing a story
            "finish the story" not in user_message and
            
            # Response is long enough
            response_word_count > 100 and
            
            # Either it's a story OR it's a data response
            (is_story_response or is_health_narrative or (is_data_response or contains_user_data))
        )
        
        # Don't add continuation prompt if we already added a conclusion
        has_conclusion = any(phrase in formatted_response.lower() for phrase in 
            ["concludes", "conclusion", "the end", "end of the story", "this concludes"])
        
        # Handle the third continuation for stories to force a conclusion
        if user_message.lower() == "continue" and "continuation_count" in st.session_state:
            if st.session_state.continuation_count >= 2:
                has_conclusion = True  # Force no continuation prompt on third continue
                if "this concludes" not in formatted_response.lower():
                    formatted_response += "\n\nThis concludes the story."
        
        # Check if we're about to cut off in the middle
        is_cut_off = response_word_count > 90 and not formatted_response.endswith(".") and not has_conclusion
        
        if (should_add_prompt or is_cut_off) and not has_conclusion and "Would you like to see more" not in formatted_response:
            formatted_response += "\n\nWould you like to see more?... (Write 'continue')"
        
        return formatted_response
        
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}"