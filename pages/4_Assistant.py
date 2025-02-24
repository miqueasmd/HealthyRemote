import streamlit as st
from utils.database import get_user_data, save_chat_message, get_chat_history
from utils.components import get_ai_response

def format_user_metrics(user_data):
    """Format user metrics and history"""
    # Get latest metrics
    latest_assessment = user_data.get('assessments', [{}])[0]
    metrics = {
        'stress': latest_assessment.get('stress_score', 'Not measured'),
        'bmi': latest_assessment.get('bmi', 'Not measured'),
        'activity_streak': len(user_data.get('activities', []))
    }
    
    # Format weight history
    weight_logs = []
    for log in user_data.get('weight_logs', []):
        weight_logs.append(f"|{log['date'].strftime('%Y-%m-%d')}|{log['weight']} kg|")
    
    # Format challenges
    challenges = []
    for challenge in user_data.get('active_challenges', []):
        progress = challenge.get('progress', {})
        day = progress.get('current_day', 1)
        tasks = progress.get('completed_tasks', [])
        challenges.append(
            f"- 🌟 **{challenge['challenge_name']}** (Day {day})\n"
            f"  - Progress: {', '.join(tasks) if tasks else 'Just started'}"
        )
    
    return metrics, weight_logs, challenges

# Page configuration
st.set_page_config(page_title="AI Wellness Assistant", page_icon="💬", layout="wide")

# Check authentication
if not st.session_state.get("authenticated", False):
    st.warning("Please login to access the AI Assistant.")
    st.stop()

# Initialize chat interface
st.title("💬 Your Personal Wellness Assistant")

# Sidebar content
with st.sidebar:
    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    # Help section
    st.markdown("""
    ### 💡 How I can help you:
    - Track your wellness metrics
    - Suggest personalized exercises
    - Provide stress management techniques
    - Guide you through meditation
    - Share work-life balance tips
    """)

# Initialize or load chat history
if "messages" not in st.session_state:
    try:
        # Get and format user data
        user_data = get_user_data(st.session_state.user_id)
        username = user_data['name']
        metrics, weight_logs, challenges = format_user_metrics(user_data)
        
        # Create initial greeting with formatted data
        initial_greeting = f"""Hello {username}! 👋  

How are you feeling today?  

### Your current wellness metrics:
- 😌 **Stress Level:** {metrics['stress']}/10  
- 🏃‍♂️ **Activity Streak:** {metrics['activity_streak']} days  
- 📊 **BMI:** {metrics['bmi']}  

### 🎯 Active Challenges:
{chr(10).join(challenges) if challenges else "No active challenges at the moment."}
"""

        # Update system prompt to properly use challenges data
        system_prompt = f"""You are a wellness assistant for {username}. 

USER DATA:
1. Current Metrics:
   - Stress: {metrics['stress']}/10
   - BMI: {metrics['bmi']}
   - Activity Streak: {metrics['activity_streak']} days

2. Active Challenges:
{chr(10).join(challenges) if challenges else "No active challenges"}

RESPONSE GUIDELINES:
1. When asked about challenges, ALWAYS check and list ALL active challenges
2. Format challenges as:
   ### 🎯 Active Challenges
   {chr(10).join(challenges) if challenges else "You don't have any active challenges at the moment."}
3. Keep responses supportive and encouraging
4. Reference specific challenge names when discussing progress"""

        # Store messages but only display the greeting
        st.session_state.messages = [
            {"role": "system", "content": system_prompt, "visible": False},
            {"role": "assistant", "content": initial_greeting, "visible": True}
        ]
        save_chat_message(st.session_state.user_id, "system", system_prompt)
        save_chat_message(st.session_state.user_id, "assistant", initial_greeting)
        
    except Exception as e:
        st.error(f"Error initializing chat: {str(e)}")
        initial_greeting = "Hello! I'm your personal wellness assistant. How can I help you today?"
        st.session_state.messages = [{"role": "assistant", "content": initial_greeting, "visible": True}]

# Display chat messages (only visible ones)
for message in st.session_state.messages:
    if message.get("visible", True):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_chat_message(st.session_state.user_id, "user", prompt)

    with st.chat_message("assistant"):
        response = get_ai_response(st.session_state.user_id, prompt)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})