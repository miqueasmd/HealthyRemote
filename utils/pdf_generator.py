from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import base64
from datetime import datetime

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
    story.append(Paragraph("Wellness Report", title_style))
    story.append(Spacer(1, 20))

    # Latest Assessment Results
    if user_data['assessments']:
        latest = user_data['assessments'][0]  # Most recent assessment
        story.append(Paragraph("Latest Assessment", styles['Heading2']))

        data = [
            ['Metric', 'Value'],
            ['Date', format_date(latest['date'])],
            ['Stress Score', f"{latest['stress_score']}/10"],
            ['BMI', f"{latest['bmi']:.1f}"],
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

    # Recommendations
    story.append(Paragraph("Recommendations", styles['Heading2']))
    for rec in user_data.get('recommendations', []):
        story.append(Paragraph(f"• {rec}", styles['Normal']))


    # Generate PDF
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    # Convert to base64 for downloading
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    return base64_pdf