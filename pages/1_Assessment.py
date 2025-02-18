import streamlit as st
import datetime
from utils.assessment import (
    calculate_stress_score,
    calculate_bmi,
    evaluate_physical_discomfort,
    calculate_activity_score
)
from utils.recommendations import (
    get_stress_recommendations,
    get_ergonomic_recommendations,
    get_activity_recommendations
)
from utils.database import save_assessment, get_assessments
from utils.components import init_spotify_player

init_spotify_player()

st.title("📋 Wellness Assessment")

# Assessment Form
with st.form("wellness_assessment"):
    st.subheader("Stress Assessment")

    work_stress = st.slider(
        "How stressed do you feel about work?",
        0, 10, 5,
        help="0 = Not stressed at all, 10 = Extremely stressed"
    )

    sleep_quality = st.slider(
        "How would you rate your sleep quality?",
        0, 10, 5,
        help="0 = Very poor, 10 = Excellent"
    )

    anxiety_level = st.slider(
        "How would you rate your anxiety level?",
        0, 10, 5,
        help="0 = No anxiety, 10 = Severe anxiety"
    )

    work_life_balance = st.slider(
        "How satisfied are you with your work-life balance?",
        0, 10, 5,
        help="0 = Very unsatisfied, 10 = Very satisfied"
    )

    st.subheader("Physical Health Assessment")

    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0)
    with col2:
        height = st.number_input("Height (m)", min_value=1.0, max_value=2.5, value=1.70)

    st.subheader("Pain Points")
    pain_areas = ['neck', 'shoulders', 'back', 'wrists', 'head']
    pain_points = {}

    col1, col2 = st.columns(2)
    for i, area in enumerate(pain_areas):
        with col1 if i % 2 == 0 else col2:
            pain_points[area] = st.selectbox(
                f"{area.title()} pain level",
                ['none', 'mild', 'moderate', 'severe'],
                key=f"pain_{area}"
            )

    st.subheader("Activity Level")
    activity_level = st.select_slider(
        "How would you describe your daily activity level?",
        options=['sedentary', 'light', 'moderate', 'vigorous'],
        value='light'
    )

    submitted = st.form_submit_button("Submit Assessment")

if submitted:
    # Calculate scores
    stress_responses = {
        'work_stress': work_stress/10,
        'sleep_quality': (10-sleep_quality)/10,  # Inverse as higher sleep quality = lower stress
        'anxiety_level': anxiety_level/10,
        'work_life_balance': (10-work_life_balance)/10  # Inverse as higher satisfaction = lower stress
    }

    stress_score = calculate_stress_score(stress_responses)
    bmi = calculate_bmi(weight, height)
    physical_evaluation = evaluate_physical_discomfort(pain_points)

    # Store assessment results in database
    assessment_data = {
        'stress_score': stress_score,
        'bmi': bmi,
        'pain_points': pain_points,
        'activity_level': activity_level,
        'physical_score': physical_evaluation['score']
    }

    save_assessment(st.session_state.user_id, assessment_data)

    # Display results
    st.success("Assessment completed!")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Stress Score", f"{stress_score}/10")
    with col2:
        st.metric("BMI", f"{bmi:.1f}")
    with col3:
        st.metric("Physical Discomfort", physical_evaluation['risk_level'])

    # Show recommendations
    st.subheader("Recommendations")

    tabs = st.tabs(["Stress Management", "Ergonomics", "Activity"])

    with tabs[0]:
        for rec in get_stress_recommendations(stress_score):
            st.write(f"• {rec}")

    with tabs[1]:
        for rec in get_ergonomic_recommendations(pain_points):
            st.write(f"• {rec}")

    with tabs[2]:
        for rec in get_activity_recommendations(bmi, activity_level):
            st.write(f"• {rec}")

# Display previous assessments
previous_assessments = get_assessments(st.session_state.user_id)
if previous_assessments:
    st.subheader("Previous Assessments")
    for assessment in previous_assessments[:5]:  # Show last 5 assessments
        with st.expander(f"Assessment from {assessment['date'].strftime('%Y-%m-%d %H:%M')}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Stress Score", f"{assessment['stress_score']}/10")
            with col2:
                st.metric("BMI", f"{assessment['bmi']:.1f}")
            with col3:
                st.metric("Activity Level", assessment['activity_level'])