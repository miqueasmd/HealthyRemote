import streamlit as st
from utils.database import get_user_data, save_chat_message, get_chat_history
from utils.components import get_ai_response, interpret_bmi

def format_user_metrics(user_data):

    # Get BMI and its category
    bmi_value = user_data['assessments'][0].get('bmi', 'N/A')
    bmi_category = interpret_bmi(bmi_value) if bmi_value != 'N/A' else 'Not available'
    
    """Format user metrics and history"""
    # Format metrics with bullet points
    metrics = f"""
- 😌 Stress Level: {user_data['assessments'][0].get('stress_score', 'N/A')}/10
- 🏃‍♂️ Activity Streak: {len(user_data.get('activities', []))} days
- 📊 BMI: {bmi_value} ({bmi_category})"""

    # Format challenges list with compact spacing
    challenges_text = []
    if user_data.get('active_challenges'):
        for ch in user_data['active_challenges']:
            challenge_title = f"- 🌟 **{ch['challenge_name']} (Day {ch['progress']['current_day']})**"
            progress_tasks = "\n  - ".join([f"✅ {task}" for task in ch['progress'].get('completed_tasks', [])])
            # Remove extra newline by directly connecting title with tasks
            challenges_text.append(f"{challenge_title}\n  - {progress_tasks}")
    
    
    # Format historical data
    historical_data = {
        'weight_logs': user_data.get('weight_logs', []),
        'stress_logs': user_data.get('stress_logs', []),
        'activities': user_data.get('activities', []),
        'assessments': user_data.get('assessments', []),
    }
    
    return metrics, historical_data, "\n".join(challenges_text)  # Remove extra newlines between challenges

# Page configuration
st.set_page_config(page_title="AI Wellness Assistant", page_icon="💬", layout="wide")

# Check authentication
if not st.session_state.get("authenticated", False):
    st.warning("Please login to access the AI Assistant.")
    st.stop()

# Initialize chat interface
st.title("💬 HealthyRemote, Your Personal Wellness Assistant")

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
    # Create a main container for messages
    message_container = st.container()
    
    # Display messages in the message container
    with message_container:
        if "messages" not in st.session_state:
            try:
                # Get user data
                user_data = get_user_data(st.session_state.user_id)
                username = user_data['name']
                metrics, historical_data, challenges_formatted = format_user_metrics(user_data)

                # Create initial greeting
                initial_greeting = f"""Hello {username}! 👋

How are you feeling today?

Your current wellness metrics:
{metrics}

🎯 Active Challenges:
{challenges_formatted if challenges_formatted else "No active challenges at the moment."}
"""
                # Initialize messages
                st.session_state.messages = [
                    {"role": "assistant", "content": initial_greeting, "visible": True}
                ]
            except Exception as e:
                st.error(f"Error initializing chat: {str(e)}")
                st.session_state.messages = [{"role": "assistant", 
                    "content": "Hello! I'm your personal wellness assistant. How can I help you today?", 
                    "visible": True}]

        # Display existing messages
        for message in st.session_state.messages:
            if message.get("visible", True):
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
    
    # Chat input at the bottom
    user_input = st.chat_input("Type your message here...")

    # Process the message when submitted
    if user_input:
        # Check if the user wants to continue
        if user_input.lower() == "continue":
            # Retrieve the last response and add user message to state
            previous_response = st.session_state.get('last_response', "")
            st.session_state.messages.append({"role": "user", "content": "continue"})
            save_chat_message(st.session_state.user_id, "user", "continue")
            
            # Track number of continuations in session state
            if 'continuation_count' not in st.session_state:
                st.session_state.continuation_count = 0
            st.session_state.continuation_count += 1
            
            # Limit continuations to prevent endless stories
            if st.session_state.continuation_count >= 2:
                # On last continuation, ask for conclusion
                response = get_ai_response(st.session_state.user_id, "Please continue but keep it concise and finish the story in this response.", previous_response)
                # Reset continuation count
                st.session_state.continuation_count = 0
            else:
                response = get_ai_response(st.session_state.user_id, user_input, previous_response)
        else:
            # Reset continuation count for new conversations
            st.session_state.continuation_count = 0
            
            # Add user message to state and display
            st.session_state.messages.append({"role": "user", "content": user_input})
            save_chat_message(st.session_state.user_id, "user", user_input)

            # Get and add AI response
            response = get_ai_response(st.session_state.user_id, user_input)
        
        # Store the last response
        st.session_state.last_response = response
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        st.rerun()

