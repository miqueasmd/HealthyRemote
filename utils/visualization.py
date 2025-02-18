import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def create_stress_trend_chart(stress_logs):
    """Create a line chart showing stress levels over time."""
    df = pd.DataFrame(stress_logs)
    
    fig = px.line(
        df,
        x='date',
        y='stress_score',
        title='Stress Level Trend',
        labels={'date': 'Date', 'stress_score': 'Stress Score'}
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        hovermode='x unified'
    )
    
    return fig

def create_activity_heatmap(activity_logs):
    """Create a heatmap showing activity patterns."""
    df = pd.DataFrame(activity_logs)
    
    fig = px.density_heatmap(
        df,
        x='day_of_week',
        y='time_of_day',
        title='Activity Pattern Heatmap',
        labels={'day_of_week': 'Day of Week', 'time_of_day': 'Time of Day'}
    )
    
    fig.update_layout(
        height=400,
        showlegend=True
    )
    
    return fig

def create_body_map(pain_points):
    """Create a visualization of pain points on body map."""
    # Using HTML/CSS for a simple body map visualization
    colors = {
        'none': '#ffffff',
        'mild': '#ffeda0',
        'moderate': '#feb24c',
        'severe': '#f03b20'
    }
    
    html = f"""
    <div style="text-align: center;">
        <svg width="200" height="400" viewBox="0 0 200 400">
            <!-- Head -->
            <circle cx="100" cy="50" r="30" fill="{colors[pain_points.get('head', 'none')]}" stroke="black"/>
            
            <!-- Neck -->
            <rect x="85" y="80" width="30" height="20" fill="{colors[pain_points.get('neck', 'none')]}" stroke="black"/>
            
            <!-- Torso -->
            <rect x="60" y="100" width="80" height="120" fill="{colors[pain_points.get('back', 'none')]}" stroke="black"/>
            
            <!-- Arms -->
            <rect x="30" y="100" width="30" height="100" fill="{colors[pain_points.get('shoulders', 'none')]}" stroke="black"/>
            <rect x="140" y="100" width="30" height="100" fill="{colors[pain_points.get('shoulders', 'none')]}" stroke="black"/>
            
            <!-- Wrists -->
            <rect x="25" y="200" width="40" height="20" fill="{colors[pain_points.get('wrists', 'none')]}" stroke="black"/>
            <rect x="135" y="200" width="40" height="20" fill="{colors[pain_points.get('wrists', 'none')]}" stroke="black"/>
        </svg>
    </div>
    """
    
    return html

def create_weight_trend_chart(weight_logs):
    """Create a line chart showing weight trend over time."""
    df = pd.DataFrame(weight_logs)
    
    fig = px.line(
        df,
        x='date',
        y='weight',
        title='Weight Trend',
        labels={'date': 'Date', 'weight': 'Weight (kg)'}
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        hovermode='x unified'
    )
    
    return fig
