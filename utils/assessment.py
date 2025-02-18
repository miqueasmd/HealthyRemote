import numpy as np

def calculate_stress_score(responses):
    """Calculate stress score based on questionnaire responses."""
    weights = {
        'work_stress': 0.3,
        'sleep_quality': 0.2,
        'anxiety_level': 0.3,
        'work_life_balance': 0.2
    }
    
    score = sum(responses[key] * weights[key] for key in weights)
    return round(score * 10)

def calculate_bmi(weight, height):
    """Calculate BMI from weight (kg) and height (m)."""
    try:
        bmi = weight / (height ** 2)
        return round(bmi, 1)
    except ZeroDivisionError:
        return 0

def evaluate_physical_discomfort(pain_points):
    """Evaluate physical discomfort based on reported pain points."""
    severity_scores = {
        'none': 0,
        'mild': 1,
        'moderate': 2,
        'severe': 3
    }
    
    total_score = sum(severity_scores[severity] for severity in pain_points.values())
    return {
        'score': total_score,
        'risk_level': 'High' if total_score > 8 else 'Medium' if total_score > 4 else 'Low'
    }

def calculate_activity_score(weekly_activities):
    """Calculate activity score based on reported activities."""
    activity_points = {
        'sedentary': 1,
        'light': 2,
        'moderate': 3,
        'vigorous': 4
    }
    
    total_points = sum(activity_points[activity] for activity in weekly_activities)
    return min(10, total_points / 2)  # Score out of 10
