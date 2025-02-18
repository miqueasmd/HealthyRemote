def get_stress_recommendations(stress_score):
    """Generate stress management recommendations based on stress score."""
    recommendations = {
        'high': [
            "Practice deep breathing exercises 3 times daily",
            "Take regular breaks every 45 minutes",
            "Consider meditation or mindfulness practices",
            "Schedule regular video calls with colleagues or friends"
        ],
        'medium': [
            "Take short walks during breaks",
            "Practice desk stretches",
            "Maintain a consistent work schedule",
            "Create a dedicated workspace"
        ],
        'low': [
            "Continue your current stress management practices",
            "Schedule regular exercise",
            "Maintain work-life boundaries",
            "Stay connected with colleagues"
        ]
    }
    
    if stress_score >= 7:
        return recommendations['high']
    elif stress_score >= 4:
        return recommendations['medium']
    else:
        return recommendations['low']

def get_ergonomic_recommendations(pain_points):
    """Generate ergonomic recommendations based on reported pain points."""
    recommendations = {
        'neck': [
            "Position screen at eye level",
            "Use a document holder",
            "Take regular neck stretching breaks"
        ],
        'shoulders': [
            "Keep elbows close to body while typing",
            "Use armrests if available",
            "Practice shoulder rolls"
        ],
        'back': [
            "Use a chair with good lumbar support",
            "Maintain proper posture",
            "Take standing breaks every hour"
        ],
        'wrists': [
            "Keep wrists straight while typing",
            "Use wrist rests",
            "Perform wrist stretches"
        ]
    }
    
    result = []
    for area, severity in pain_points.items():
        if severity != 'none' and area in recommendations:
            result.extend(recommendations[area])
    return result

def get_activity_recommendations(bmi, activity_level):
    """Generate activity recommendations based on BMI and current activity level."""
    base_recommendations = [
        "Aim for 150 minutes of moderate activity per week",
        "Include both cardio and strength training",
        "Take regular walking breaks during work hours",
        "Set up a standing desk if possible"
    ]
    
    if bmi >= 25:
        base_recommendations.extend([
            "Focus on low-impact activities initially",
            "Gradually increase activity duration",
            "Consider consulting a healthcare provider"
        ])
    
    if activity_level == 'sedentary':
        base_recommendations.extend([
            "Start with 5-10 minute walking breaks",
            "Try desk exercises",
            "Set hourly movement reminders"
        ])
        
    return base_recommendations
