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
    
    # Format challenges list with proper indentation
    challenges_text = []
    if user_data.get('active_challenges'):
        for ch in user_data['active_challenges']:
            challenge_title = f"- 🌟 **{ch['challenge_name']} (Day {ch['progress']['current_day']})**"
            progress_tasks = "\n  - ".join([f"✅ {task}" for task in ch['progress'].get('completed_tasks', [])])
            challenges_text.append(f"{challenge_title}\n  - {progress_tasks}")
    
    
    # Format historical data
    historical_data = {
        'weight_logs': user_data.get('weight_logs', []),
        'stress_logs': user_data.get('stress_logs', []),
        'activities': user_data.get('activities', []),
        'assessments': user_data.get('assessments', []),
    }
    
    return metrics, historical_data, "\n\n".join(challenges_text)  # Add extra newline for separation

# Page configuration
st.set_page_config(page_title="AI Wellness Assistant", page_icon="💬", layout="wide")

# Check authentication
if not st.session_state.get("authenticated", False):
    st.warning("Please login to access the AI Assistant.")
    st.stop()

# Initialize chat interface
st.title("💬 Your Personal Wellness Assistant")

# Create two columns for layout
col1, col2 = st.columns([2, 1])

# Right column: Records Viewer
with col2:
    st.info("📊 Records Viewer")
    records_option = st.selectbox(
        "Select record type:",
        ["Weight History", "Stress History", "Activity History", "Active Challenges"]
    )

    user_data = get_user_data(st.session_state.user_id)
    metrics, historical_data, challenges = format_user_metrics(user_data)

    # Display selected record type
    if records_option == "Weight History":
        if historical_data['weight_logs']:
            st.markdown("### ⚖️ Weight History")
            st.dataframe(
                [{"Date": w['date'].strftime('%Y-%m-%d'), 
                  "Weight (kg)": w['weight']} 
                 for w in historical_data['weight_logs']],
                hide_index=True
            )
        else:
            st.info("No weight records found.")
            
    elif records_option == "Stress History":
        if historical_data['stress_logs']:
            st.markdown("### 😌 Stress History")
            st.dataframe(
                [{"Date": s['date'].strftime('%Y-%m-%d'), 
                  "Stress Level": f"{s['stress_score']}/10"} 
                 for s in historical_data['stress_logs']],
                hide_index=True
            )
        else:
            st.info("No stress records found.")
            
    elif records_option == "Activity History":
        if historical_data['activities']:
            st.markdown("### 🏃‍♂️ Activity History")
            st.dataframe(
                [{"Date": a['date'].strftime('%Y-%m-%d'),
                  "Activity": a['activity_type'],  # Changed from 'type' to 'activity_type'
                  "Duration": f"{a['duration']} min"} 
                 for a in historical_data['activities']],
                hide_index=True
            )
        else:
            st.info("No activity records found.")
            
    elif records_option == "Active Challenges":
        # Re-fetch user data and formatted challenges
        user_data = get_user_data(st.session_state.user_id)
        metrics, historical_data, challenges_formatted = format_user_metrics(user_data)

        if challenges_formatted.strip():  # Ensure it's not empty
            st.markdown("### 🎯 Active Challenges")
            st.markdown(challenges_formatted)
        else:
            st.info("No active challenges found.")

# Left column: Chat Interface
with col1:
    if "messages" not in st.session_state:
        try:
            # Get user data
            user_data = get_user_data(st.session_state.user_id)
            username = user_data['name']
            metrics, historical_data, challenges_formatted = format_user_metrics(user_data)

            # Create initial greeting with properly formatted challenges
            initial_greeting = f"""Hello {username}! 👋

How are you feeling today?

Your current wellness metrics:
😌 Stress Level: {metrics['stress']}/10
🏃‍♂️ Activity Streak: {metrics['activity_streak']} days
📊 BMI: {metrics['bmi']}

🎯 Active Challenges:
{challenges_formatted if challenges_formatted else "No active challenges at the moment."}
"""
            # Store messages
            st.session_state.messages = [
                {"role": "assistant", "content": initial_greeting, "visible": True}
            ]
            
        except Exception as e:
            st.error(f"Error initializing chat: {str(e)}")
            st.session_state.messages = [{"role": "assistant", 
                "content": "Hello! I'm your personal wellness assistant. How can I help you today?", 
                "visible": True}]

    # Display chat messages
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
            # Check if it's a records request
            if any(keyword in prompt.lower() for keyword in ["show records", "show history", "weight history", "stress history"]):
                # Get fresh data
                user_data = get_user_data(st.session_state.user_id)
                metrics, historical_data, challenges = format_user_metrics(user_data)
                
                if "weight" in prompt.lower():
                    response = """Here are your weight records:
                    ```markdown
                    | Date | Weight (kg) |
                    |------|------------|
                    {}
                    ```
                    """.format('\n'.join([
                        f"|{w['date'].strftime('%Y-%m-%d')}|{w['weight']}|" 
                        for w in historical_data['weight_logs']
                    ]))
                else:
                    # Let AI handle other responses
                    response = get_ai_response(st.session_state.user_id, prompt)
            else:
                response = get_ai_response(st.session_state.user_id, prompt)
                
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

