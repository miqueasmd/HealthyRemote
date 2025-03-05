import streamlit as st
import pandas as pd
from utils.visualization import (
    create_stress_trend_chart,
    create_activity_heatmap,
    create_weight_trend_chart
)
from utils.recommendations import (
    get_stress_recommendations,
    get_ergonomic_recommendations,
    get_activity_recommendations
)
from utils.database import (
    get_stress_logs,
    get_activities,
    get_weight_logs,
    save_stress_log,
    save_activity,
    save_weight_log,
    get_assessments,
    get_active_challenges,
    get_db_connection #Added this import
)
from utils.pdf_generator import generate_wellness_report
import json
from json import JSONEncoder

from utils.components import init_spotify_player, interpret_bmi

init_spotify_player()

class GetEncoder(JSONEncoder):
    def default(self, obj):
        return obj.__dict__

Json = GetEncoder()

st.title("📈 Progress Tracking")

# Get user data from database
stress_logs = get_stress_logs(st.session_state.user_id)
activities = get_activities(st.session_state.user_id)
weight_logs = get_weight_logs(st.session_state.user_id)
assessments = get_assessments(st.session_state.user_id)

if assessments:
    # Create tabs for different metrics
    tabs = st.tabs(["Stress Levels", "Physical Activity", "Weight Tracking", "Active Challenges"])

    with tabs[0]:
        if stress_logs:
            st.plotly_chart(create_stress_trend_chart(stress_logs), use_container_width=True)

        # Add new stress log
        with st.expander("Log Today's Stress Level"):
            stress_level = st.slider("Stress Level", 0, 10, 5)
            if st.button("Log Stress"):
                save_stress_log(st.session_state.user_id, stress_level)
                st.success("Stress level logged!")
                st.rerun()

    with tabs[1]:
        if activities:
            activity_df = pd.DataFrame(activities)
            activity_df['day_of_week'] = pd.to_datetime(activity_df['date']).dt.day_name()
            activity_df['time_of_day'] = pd.to_datetime(activity_df['date']).dt.hour
            st.plotly_chart(create_activity_heatmap(activity_df), use_container_width=True)

        # Log new activity
        with st.expander("Log Activity"):
            col1, col2 = st.columns(2)
            with col1:
                activity_type = st.selectbox(
                    "Activity Type",
                    ['Walking', 'Stretching', 'Exercise', 'Standing']
                )
            with col2:
                duration = st.number_input("Duration (minutes)", min_value=5, max_value=180, value=15)

            if st.button("Log Activity"):
                activity_data = {
                    'activity_type': activity_type.lower(),  # Store in lowercase for consistency
                    'duration': duration
                }
                save_activity(st.session_state.user_id, activity_data)
                st.success("Activity logged!")
                st.rerun()

    with tabs[2]:
        if weight_logs:
            st.plotly_chart(create_weight_trend_chart(weight_logs), use_container_width=True)

        # Log new weight
        with st.expander("Log Weight"):
            weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0)
            if st.button("Log Weight"):
                save_weight_log(st.session_state.user_id, weight)
                st.success("Weight logged!")
                st.rerun()

    with tabs[3]:
        st.subheader("🎯 Active Challenges")
        active_challenges = get_active_challenges(st.session_state.user_id)

        if active_challenges:
            for challenge in active_challenges:
                with st.expander(f"🌟 {challenge['challenge_name']}"):
                    progress = challenge['progress']
                    st.write(f"**Started**: {challenge['start_date'].strftime('%Y-%m-%d')}")
                    st.write(f"**Ends**: {challenge['end_date'].strftime('%Y-%m-%d')}")
                    st.write(f"**Current Day**: {progress['current_day']}")

                    # Show completed tasks
                    st.write("**Completed Tasks:**")
                    for task in progress['completed_tasks']:
                        st.write(f"✅ {task}")

                    # Add task completion button
                    new_task = st.text_input("Add completed task:", key=f"task_{challenge['id']}")
                    if st.button("Mark Complete", key=f"complete_{challenge['id']}"):
                        progress['completed_tasks'].append(new_task)
                        progress['current_day'] = min(progress['current_day'] + 1, 
                                                    (challenge['end_date'] - challenge['start_date']).days + 1)
                        # Update challenge progress in database
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute("""
                            UPDATE challenges 
                            SET progress = %s 
                            WHERE id = %s
                        """, (json.dumps(progress), challenge['id'])) # use json.dumps instead of Json
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.rerun()
        else:
            st.info("No active challenges. Start a new challenge in the Education section!")

    # Generate report
    st.subheader("Progress Report")
    if st.button("Generate PDF Report"):
        latest_assessment = assessments[0]  # Most recent assessment
        recommendations = []
        recommendations.extend(get_stress_recommendations(latest_assessment['stress_score']))
        recommendations.extend(get_ergonomic_recommendations(latest_assessment['pain_points']))
        recommendations.extend(get_activity_recommendations(latest_assessment['bmi'], latest_assessment['activity_level']))

        user_data = {
            'assessments': assessments,
            'stress_logs': stress_logs,
            'activities': activities,
            'weight_logs': weight_logs,
            'recommendations': recommendations
        }

        try:
            pdf_base64 = generate_wellness_report(user_data)
            href = f'<a href="data:application/pdf;base64,{pdf_base64}" download="wellness_report.pdf">Download PDF Report</a>'
            st.markdown(href, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error generating PDF report: {e}")

else:
    st.info("👈 Start by taking your first assessment in the Assessment section!")