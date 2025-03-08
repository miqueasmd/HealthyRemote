import streamlit as st
from typing import List, Dict
from openai import OpenAI
from .database import save_chat_message, get_chat_history, get_user_data
import re

def init_spotify_player():
    """Initialize Spotify player in sidebar"""
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
    """Generate AI response to user message with context awareness"""
    try:
        client = OpenAI()
        
        # Get comprehensive user data
        user_data = get_user_data(user_id)
        
        # Check if this is a continuation request
        is_continuation_request = ("continue" in user_message.lower() or 
                                  user_message.lower() in ["more", "go on", "what's next", "proceed", "continuar"])
                                  
        # If it's a continuation and we have stored content, return that
        if is_continuation_request and "remaining_response" in st.session_state:
            formatted_response = st.session_state.remaining_response
            del st.session_state.remaining_response
            return formatted_response
            
        # Create conversation context from chat history
        conversation_history = user_data.get('chat_history', [])
        # Take only the last 15 messages to avoid token limits
        recent_history = conversation_history[-15:] if len(conversation_history) > 15 else conversation_history
        
        # Check if user is asking about "my story" or "my health journey"
        is_asking_about_health_journey = any(phrase in user_message.lower() for phrase in 
            ["my journey", "my health journey", "my progress", "my health progress", "my data story"])
        
        # Get BMI value and interpretation
        bmi_value = user_data['assessments'][0]['bmi'] if user_data['assessments'] else 'No data'
        bmi_category = interpret_bmi(bmi_value) if bmi_value != 'No data' else 'No data'
        
        # Add comprehensive assessment history
        assessment_history = "\n".join([
            f"- Date: {a['date'].strftime('%Y-%m-%d')}, Stress Score: {a.get('stress_score', 'N/A')}, " + 
            f"BMI: {a.get('bmi', 'N/A')} ({interpret_bmi(a.get('bmi', 'N/A'))})"
            for a in user_data['assessments']
        ])
        
        # Build system message with user data context
        system_content = f"""You are HealthyRemote, a wellness assistant for {user_data['name']}. 
You have access to their complete health records, previous conversation context, and previous assessments:

1. Weight History: {[f"{w['date'].strftime('%Y-%m-%d')}: {w['weight']}kg" for w in user_data['weight_logs']]}
2. Latest Assessment:
   - Stress Score: {user_data['assessments'][0]['stress_score'] if user_data['assessments'] else 'No data'}
   - BMI: {bmi_value} ({bmi_category})
3. Assessment History:
{assessment_history}
4. Activity History: {len(user_data['activities'])} activities recorded
5. Stress History: {[f"{s['date'].strftime('%Y-%m-%d')}: {s['stress_score']}/10" for s in user_data['stress_logs']]}
6. Active Challenges: {[c['challenge_name'] for c in user_data['active_challenges']]}

Important formatting instructions:
- Keep paragraphs short (2-4 sentences max)
- Add line breaks between paragraphs
- When asked to "continue", always reference what was previously discussed and provide additional relevant information
- When providing user data or health information, always format it clearly with headers and line breaks
- When discussing the user's health journey, provide insights based on their data in a supportive, encouraging manner"""

        system_content += "\n\nWhen talking about 'my journey' or 'my health journey', the user is referring to their personal health data and progress. Provide meaningful insights and patterns from their data."
            
        system_message = {
            "role": "system",
            "content": system_content
        }
        
        messages = [system_message]
        
        # Handle different message types based on context
        if is_asking_about_health_journey:
            messages.append({"role": "user", "content": user_message})
            messages.append({"role": "system", "content": "Analyze the user's health data to create a meaningful summary of their wellness journey. Include key trends, improvements, and areas that may need attention. Be supportive and encouraging."})
            
        elif is_continuation_request and previous_response:
            # Get last response and tell the API to continue from there
            messages.append({"role": "assistant", "content": previous_response})
            messages.append({"role": "system", "content": 
                "Continue providing information on the previous topic. Add more details, recommendations, or analysis as appropriate."
            })
            messages.append({"role": "user", "content": "Please continue with more information on this topic."})
            
        else:
            # Check for specific request types to customize instructions
            is_data_request = any(phrase in user_message.lower() for phrase in
                ["my data", "my information", "my records", "my history", "my assessments", "my logs", 
                 "info about me", "tell me about me", "everything about me", "all the info", "all my data"])
            
            if is_data_request:
                messages.append({"role": "user", "content": user_message})
                messages.append({"role": "system", "content": "Provide the user's data in a clear, organized format with headers and bullet points. Include all relevant information from their health records."})
            else:
                messages.append({"role": "user", "content": user_message})
        
        # Generate response with 300 tokens
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )
        
        response_text = response.choices[0].message.content
        finish_reason = response.choices[0].finish_reason
        
        # Process response for better formatting
        formatted_response = format_response_text(response_text)
        
        # Detect user language (simple approach)
        is_spanish = any(word in user_message.lower() for word in 
                      ["como", "qué", "porque", "gracias", "hola", "por favor", "puedes", "continuar"])
        
        # Create continuation message based on language
        continue_message = "¿Quieres ver más?... (Escribe 'continuar')" if is_spanish else "Would you like to see more?... (Write 'continue')"
        
        # Handle response continuation
        needs_continuation = False
        
        # Case 1: API indicates response was cut off
        if finish_reason == "length":
            needs_continuation = True
        # Case 2: Our heuristics suggest the response might be incomplete
        elif should_add_continuation_prompt(formatted_response, user_message) and "Would you like to see more" not in formatted_response:
            needs_continuation = True
            
        # Generate and store continuation if needed
        if needs_continuation:
            # Generate the continuation response
            continuation_messages = messages.copy()
            continuation_messages.append({"role": "assistant", "content": response_text})
            continuation_messages.append({"role": "system", "content": "Continue the previous response with additional relevant details."})
            continuation_messages.append({"role": "user", "content": "Please continue with more information."})
            
            continuation_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=continuation_messages,
                temperature=0.7,
                max_tokens=300
            )
            
            # Store continuation for when user asks for more
            st.session_state.remaining_response = format_response_text(continuation_response.choices[0].message.content)
            
            # Add continuation prompt to original response
            if "Would you like to see more" not in formatted_response and "¿Quieres ver más?" not in formatted_response:
                formatted_response += f"\n\n{continue_message}"

        return formatted_response
        
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}"

def format_response_text(response_text):
    """Format the AI response for better readability"""
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
    return '\n\n'.join(formatted_paragraphs)

def should_add_continuation_prompt(formatted_response, user_message):
    """Determine if we should add a continuation prompt"""
    # Calculate response length
    response_word_count = len(formatted_response.split())
    
    # Comprehensive list of conclusion and completion phrases
    data_completion_phrases = [
        "that's all the information", "this completes your data", "those are all your records",
        "if you have any questions", "if you need any further", "if you have any specific questions",
        "feel free to ask", "i'm here to help", "i am here to help", "here to help",
        "happy to assist", "i'm here if you", "hope this helps", "let me know if"
    ]
    
    # Check response characteristics
    is_health_narrative = any(phrase in user_message.lower() for phrase in 
        ["my journey", "health journey", "progress", "narrative"])
        
    is_data_response = any(term in user_message.lower() for term in [
        "records", "assessments", "logs", "data", "weight", "stress", "activities", 
        "info", "everything", "about me", "know about me", "information"
    ])
        
    contains_user_data = any(term in formatted_response.lower() for term in 
        ["bmi", "stress score", "stress level", "weight", "kg", "assessment", "challenge"])
        
    is_emotional_response = any(term in user_message.lower() for term in 
        ["sad", "angry", "upset", "depressed", "anxious", "feeling down", "not well", "tired", "exhausted", "help me"])
    
    # Comprehensive checks for response completeness
    is_data_complete = any(phrase in formatted_response.lower() for phrase in data_completion_phrases)
    is_complete_thought = formatted_response.rstrip().endswith(('.', '?', '!'))
    ends_with_data_item = bool(re.search(r'(\d+\.|\d+\)|\d+kg|/10|\(\w+\))$', formatted_response.strip()))
    
    # Check for closing phrases
    has_closing_phrase = (
        formatted_response.rstrip().endswith(('Thank you.', 'You\'re welcome.', 'No problem.', 
                                           'Feel free to ask.', 'Let me know if you need anything else.')) or
        any(phrase in formatted_response.lower()[-50:] for phrase in 
            ['i\'m here to help', 'here to help', 'here to assist', 'happy to assist', 
             'feel free to ask', 'let me know if', 'i\'m available'])
    )
    
    # Check specifically for phrases that indicate the conclusion is the last 100 characters
    has_conclusive_ending = any(phrase in formatted_response.lower()[-100:] for phrase in 
        ["here to help", "happy to assist", "hope this helps", "let me know if", "feel free to", "i'm here", "i am here"])
    
    # Check if the response appears to be cut off
    is_cut_off = response_word_count > 90 and not is_complete_thought and not (is_data_complete or has_closing_phrase)
    
    # Decision logic for adding continuation prompt
    should_add_prompt = (
        "finish" not in user_message.lower() and
        not is_data_complete and
        not has_closing_phrase and
        not has_conclusive_ending and
        not ends_with_data_item and
        response_word_count >= 100 and
        (is_health_narrative or 
         (is_data_response and contains_user_data and response_word_count > 150)) and
        not is_emotional_response
    )
    
    return should_add_prompt or is_cut_off

def interpret_bmi(bmi_value):
    """Return interpretation of BMI value"""
    try:
        bmi = float(bmi_value)
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal weight"
        elif bmi < 30:
            return "Overweight"
        elif bmi < 35:
            return "Obesity class I"
        elif bmi < 40:
            return "Obesity class II"
        else:
            return "Obesity class III"
    except (ValueError, TypeError):
        return "Unknown"