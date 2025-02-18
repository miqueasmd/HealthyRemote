
import streamlit as st
import random
from data.wellness_tips import (
    DAILY_TIPS, 
    ERGONOMIC_GUIDELINES, 
    STRETCHING_EXERCISES,
    WELLNESS_CHALLENGES,
    MOBILITY_TESTS
)
from utils.database import save_mobility_test, start_challenge

from utils.components import init_spotify_player

init_spotify_player()

st.title("📚 Education & Resources")

# Create tabs for different sections
tabs = st.tabs(["Daily Tips", "Exercises & Videos", "Mobility Tests", "Challenges"])

with tabs[0]:
    # Daily Tip
    st.subheader("💡 Tip of the Day")
    category = random.choice(DAILY_TIPS)
    tip = random.choice(category['tips'])
    st.info(f"**{category['category']}**: {tip}")

    # Ergonomic Guidelines
    st.subheader("🪑 Ergonomic Workspace Setup")
    ergonomic_tabs = st.tabs(list(ERGONOMIC_GUIDELINES.keys()))

    for tab, (section, guidelines) in zip(ergonomic_tabs, ERGONOMIC_GUIDELINES.items()):
        with tab:
            for guideline in guidelines:
                st.write(f"• {guideline}")

with tabs[1]:
    st.subheader("🤸‍♂️ Exercise Demonstrations")

    for exercise in STRETCHING_EXERCISES:
        with st.expander(f"{exercise['name']} 🎥"):
            # Create a container with custom CSS for the video
            st.markdown(
                f"""
                <div style="display: flex; gap: 20px; align-items: start;">
                    <div style="flex: 0 0 auto;">
                        <iframe 
                            width="280" 
                            height="500" 
                            src="https://www.youtube.com/embed/{exercise['video_id']}" 
                            frameborder="0" 
                            allowfullscreen
                            style="border-radius: 12px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"
                        ></iframe>
                    </div>
                    <div style="flex: 1;">
                        <h4 style="margin-top: 0; margin-bottom: 10px;">Instructions:</h4>
                        <ul style="list-style-type: none; padding-left: 0;">
                            {"".join(f'<li style="margin: 10px 0;">• {step}</li>' for step in exercise['instructions'])}
                        </ul>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

with tabs[2]:
    st.subheader("📊 Mobility Self-Assessment")
    st.write("Complete these tests to assess your current mobility levels. Track your progress over time.")

    for test in MOBILITY_TESTS:
        with st.expander(f"🔍 {test['name']}"):
            st.write(f"**Purpose**: {test['description']}")

            st.subheader("Instructions:")
            for instruction in test['instructions']:
                st.write(f"• {instruction}")

            st.subheader("Rate Your Performance:")
            score = st.selectbox(
                "How would you rate your performance?",
                list(test['scoring'].keys()),
                key=f"mobility_{test['name']}"
            )

            notes = st.text_area(
                "Additional Notes (optional):",
                key=f"notes_{test['name']}"
            )

            if st.button("Save Results", key=f"save_{test['name']}"):
                test_data = {
                    'test_name': test['name'],
                    'score': score,
                    'notes': notes
                }
                save_mobility_test(st.session_state.user_id, test_data)
                st.success("Test results saved! Track your progress in the Progress section.")

with tabs[3]:
    st.subheader("🎯 Wellness Challenges")
    st.write("Join these challenges to improve your daily wellness habits!")

    for challenge in WELLNESS_CHALLENGES:
        with st.expander(f"🌟 {challenge['name']} ({challenge['duration']} days)"):
            st.write(f"**Description**: {challenge['description']}")

            st.subheader("Daily Tasks:")
            for task in challenge['daily_tasks']:
                st.write(f"• {task}")

            if st.button(f"Start {challenge['name']}", key=f"start_{challenge['name']}"):
                start_challenge(st.session_state.user_id, challenge)
                st.success("Challenge accepted! Track your progress in the Progress section.")

# Additional Resources
st.subheader("📚 Additional Resources")
st.markdown("""
* [CDC Workplace Health Promotion](https://www.cdc.gov/workplacehealthpromotion/index.html)
* [OSHA Computer Workstation Checklist](https://www.osha.gov/SLTC/etools/computerworkstations/checklist.html)
* [Mental Health America - Work Health Balance](https://www.mhanational.org/work-life-balance)
""")
