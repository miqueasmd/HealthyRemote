from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import base64
from datetime import datetime
from utils.components import interpret_bmi
import streamlit as st

def format_date(date_obj):
    """Format datetime object to string."""
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime("%Y-%m-%d %H:%M")

def generate_wellness_report(user_data):
    """Generate a PDF wellness report."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    
    # Get the username
    username = st.session_state.get("username", user_data.get("name", "User"))
    report_title = f"{username}'s Wellness Report"
    story.append(Paragraph(report_title, title_style))
    story.append(Spacer(1, 20))

    # Latest Assessment Results
    if user_data['assessments']:
        latest = user_data['assessments'][0]  # Most recent assessment
        story.append(Paragraph("Latest Assessment", styles['Heading2']))
        
        # Get BMI interpretation
        bmi_value = latest['bmi']
        bmi_category = interpret_bmi(bmi_value)

        data = [
            ['Metric', 'Value'],
            ['Date', format_date(latest['date'])],
            ['Stress Score', f"{latest['stress_score']}/10"],
            ['BMI', f"{latest['bmi']:.1f} ({bmi_category})"],
            ['Activity Level', latest['activity_level']],
            ['Physical Score', str(latest['physical_score'])]
        ]

        t = Table(data, colWidths=[200, 200])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(t)
        story.append(Spacer(1, 20))

    # Stress Logs
    if user_data['stress_logs']:
        story.append(Paragraph("Recent Stress Logs", styles['Heading2']))
        stress_data = [['Date', 'Stress Score']]
        for log in user_data['stress_logs'][:5]:  # Show last 5 logs
            stress_data.append([
                format_date(log['date']),
                f"{log['stress_score']}/10"
            ])

        stress_table = Table(stress_data, colWidths=[200, 200])
        stress_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(stress_table)
        story.append(Spacer(1, 20))

    # Activities
    if user_data['activities']:
        story.append(Paragraph("Recent Activities", styles['Heading2']))
        activity_data = [['Date', 'Type', 'Duration (min)']]
        for activity in user_data['activities'][:5]:
            activity_data.append([
                format_date(activity['date']),
                activity['activity_type'],
                str(activity['duration'])
            ])

        activity_table = Table(activity_data, colWidths=[133, 133, 133])
        activity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(activity_table)
        story.append(Spacer(1, 20))

    # Weight Logs
    if user_data['weight_logs']:
        story.append(Paragraph("Weight History", styles['Heading2']))
        weight_data = [['Date', 'Weight (kg)']]
        for log in user_data['weight_logs'][:5]:
            weight_data.append([
                format_date(log['date']),
                f"{log['weight']:.1f}"
            ])

        weight_table = Table(weight_data, colWidths=[200, 200])
        weight_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(weight_table)
    
    # BMI Information Section
    story.append(Spacer(1, 20))
    story.append(Paragraph("Understanding Your BMI", styles['Heading2']))

    # Create intro paragraph
    intro_text = "Body Mass Index (BMI) is a screening tool that can help indicate whether a person might be at an unhealthy weight."
    story.append(Paragraph(intro_text, styles['Normal']))
    story.append(Spacer(1, 10))

    # Create categories header
    story.append(Paragraph("BMI categories are generally defined as:", styles['Normal']))

    # Create bullet styles with more precise control
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,  # Line height
        leftIndent=30,  # Slightly more indent
        firstLineIndent=-15,
        spaceBefore=3,  # Add a tiny bit of space before each bullet
        spaceAfter=3    # Add a tiny bit of space after each bullet
    )

    # Add each bullet point as a separate paragraph
    bmi_categories = [
        "• Under 18.5: Underweight - May indicate nutritional deficiency",
        "• 18.5-24.9: Normal weight - Generally associated with good health",
        "• 25-29.9: Overweight - May increase risk of certain health conditions",
        "• 30-34.9: Obesity class I - Associated with higher health risks",
        "• 35-39.9: Obesity class II - Associated with high health risks",
        "• 40 and above: Obesity class III - Associated with very high health risks"
    ]

    for category in bmi_categories:
        story.append(Paragraph(category, bullet_style))

    # Add conclusion paragraph
    conclusion_text = """BMI is just one screening tool and doesn't account for factors like muscle mass, bone density, or fat distribution.
    It should be considered alongside other health metrics and your overall wellness."""
    story.append(Spacer(1, 10))
    story.append(Paragraph(conclusion_text, styles['Normal']))
    story.append(Spacer(1, 15))

    # Recommendations
    story.append(Paragraph("Recommendations", styles['Heading2']))
    story.append(Spacer(1, 5))  # Smaller space after heading

    for rec in user_data.get('recommendations', []):
        story.append(Paragraph(f"• {rec}", bullet_style))  # Use the same bullet style here


    # Generate PDF
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    # Convert to base64 for downloading
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    return base64_pdf