import streamlit as st
from utils.database import get_user_data, save_chat_message, get_chat_history
from utils.components import get_ai_response

# Page configuration
st.set_page_config(page_title="AI Wellness Assistant", page_icon="💬", layout="wide")

# Check authentication
if not st.session_state.get("authenticated", False):
    st.warning("Please login to access the AI Assistant.")
    st.stop()

# Initialize chat interface
st.title("💬 Your Personal Wellness Assistant")

# Clear old messages if user wants to start fresh
if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

# Initialize or load chat history
if "messages" not in st.session_state:
    try:
        # Get user data for personalized greeting
        user_data = get_user_data(st.session_state.user_id)
        username = user_data.get('name')
        st.session_state.username = username  # Store username in session state
        
        # Create initial greeting with user's name and data
        initial_greeting = f"""Hello {username}! 👋 

How are you feeling today?

Your current wellness metrics:
• 😌 Stress Level: {user_data.get('assessments', [{}])[0].get('stress_score', 'Not measured yet') if user_data.get('assessments') else 'Not measured yet'}/10
• 🏃‍♂️ Activity Streak: {len(user_data.get('activities', []))} days
• 📊 BMI: {user_data.get('assessments', [{}])[0].get('bmi', 'Not measured yet') if user_data.get('assessments') else 'Not measured yet'}

Let me know if you need any support or guidance!"""

        # Initialize chat with stronger system context
        system_prompt = f"""You are a wellness assistant for {username}. 
CRITICAL INSTRUCTIONS:
1. The user's name is '{username}' - ALWAYS use this name
2. If asked about their name, respond with: "Yes, I know you're {username}!"
3. Use their name naturally in responses
4. Keep track of their metrics and reference them when relevant
5. Maintain a supportive and personalized tone"""

        st.session_state.messages = [
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": initial_greeting}
        ]
        save_chat_message(st.session_state.user_id, "system", system_prompt)
        save_chat_message(st.session_state.user_id, "assistant", initial_greeting)
        
    except Exception as e:
        st.error(f"Error initializing chat: {str(e)}")
        initial_greeting = "Hello! I'm your personal wellness assistant. How can I help you today?"
        st.session_state.messages = [{"role": "assistant", "content": initial_greeting}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_chat_message(st.session_state.user_id, "user", prompt)

    # Get and display assistant response
    with st.chat_message("assistant"):
        response = get_ai_response(st.session_state.user_id, prompt)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Helpful sidebar tips
with st.sidebar:
    st.markdown("""
    ### 💡 How I can help you:
    - Track your wellness metrics
    - Suggest personalized exercises
    - Provide stress management techniques
    - Guide you through meditation
    - Share work-life balance tips
    """)