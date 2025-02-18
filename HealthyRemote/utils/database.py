import os
import pandas as pd
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor, Json

# Add this at the top of the file
DEFAULT_DB_URL = "postgresql://neondb_owner:npg_RAS5tzxGNUH1@ep-aged-mouse-a95y9tli-pooler.gwc.azure.neon.tech/neondb?sslmode=require"

def get_user_by_email(email):
    """Get user by email address."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id FROM users 
        WHERE email = %s
    """, (email,))

    user = cur.fetchone()
    cur.close()
    conn.close()

    return user['id'] if user else None

def create_new_user(name, email):
    """Create a new user with name and email."""
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO users (name, email) 
            VALUES (%s, %s)
            RETURNING id
        """, (name, email))

        user_id = cur.fetchone()['id']
        conn.commit()
        return user_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def get_db_connection():
    """Create a database connection."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables")
    print(f"Connecting to: {database_url}")  # For debugging
    return psycopg2.connect(
        database_url,
        cursor_factory=RealDictCursor
    )

def init_db():
    """Initialize the database tables."""
    conn = get_db_connection()
    cur = conn.cursor()

    # Create users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            email VARCHAR(255) UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create assessments table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            stress_score INTEGER,
            bmi FLOAT,
            activity_level VARCHAR(50),
            physical_score INTEGER,
            pain_points JSONB,
            CONSTRAINT stress_score_range CHECK (stress_score BETWEEN 0 AND 10)
        )
    """)

    # Create activities table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            activity_type VARCHAR(50),
            duration INTEGER,
            CONSTRAINT duration_check CHECK (duration > 0)
        )
    """)

    # Create stress_logs table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stress_logs (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            stress_score INTEGER,
            CONSTRAINT stress_log_score_range CHECK (stress_score BETWEEN 0 AND 10)
        )
    """)

    # Create weight_logs table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS weight_logs (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            weight FLOAT,
            CONSTRAINT weight_check CHECK (weight > 0)
        )
    """)

    # Handle mobility_tests table creation
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS mobility_tests (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                test_name VARCHAR(50),
                score VARCHAR(50),
                notes TEXT
            )
        """)
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        # Table already exists, skip creation

    # Handle challenges table creation
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS challenges (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                challenge_name VARCHAR(100),
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_date TIMESTAMP,
                status VARCHAR(20) DEFAULT 'active',
                progress JSONB
            )
        """)
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        # Table already exists, skip creation

    conn.commit()
    cur.close()
    conn.close()

def get_or_create_user():
    """This function is kept for backward compatibility."""
    conn = get_db_connection()
    cur = conn.cursor()

    # For now, we'll just create a new user if none exists
    cur.execute("SELECT id FROM users WHERE name IS NULL LIMIT 1")
    user = cur.fetchone()

    if not user:
        cur.execute("INSERT INTO users DEFAULT VALUES RETURNING id")
        user = cur.fetchone()
        conn.commit()

    user_id = user['id']
    cur.close()
    conn.close()
    return user_id

def save_assessment(user_id, assessment_data):
    """Save an assessment to the database."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO assessments 
        (user_id, stress_score, bmi, activity_level, physical_score, pain_points)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        user_id,
        assessment_data['stress_score'],
        assessment_data['bmi'],
        assessment_data['activity_level'],
        assessment_data['physical_score'],
        Json(assessment_data['pain_points'])  # Convert dict to JSON
    ))

    assessment_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    return assessment_id

def get_assessments(user_id):
    """Get all assessments for a user."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM assessments 
        WHERE user_id = %s 
        ORDER BY date DESC
    """, (user_id,))

    assessments = cur.fetchall()
    cur.close()
    conn.close()
    return assessments

def save_activity(user_id, activity_data):
    """Save an activity to the database."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO activities 
        (user_id, activity_type, duration)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (
        user_id,
        activity_data['activity_type'],  
        activity_data['duration']
    ))

    activity_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    return activity_id

def get_activities(user_id):
    """Get all activities for a user."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM activities 
        WHERE user_id = %s 
        ORDER BY date DESC
    """, (user_id,))

    activities = cur.fetchall()
    cur.close()
    conn.close()
    return activities

def save_stress_log(user_id, stress_score):
    """Save a stress log entry."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO stress_logs 
        (user_id, stress_score)
        VALUES (%s, %s)
        RETURNING id
    """, (user_id, stress_score))

    log_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    return log_id

def get_stress_logs(user_id):
    """Get all stress logs for a user."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM stress_logs 
        WHERE user_id = %s 
        ORDER BY date DESC
    """, (user_id,))

    logs = cur.fetchall()
    cur.close()
    conn.close()
    return logs

def save_weight_log(user_id, weight):
    """Save a weight log entry."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO weight_logs 
        (user_id, weight)
        VALUES (%s, %s)
        RETURNING id
    """, (user_id, weight))

    log_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    return log_id

def get_weight_logs(user_id):
    """Get all weight logs for a user."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM weight_logs 
        WHERE user_id = %s 
        ORDER BY date DESC
    """, (user_id,))

    logs = cur.fetchall()
    cur.close()
    conn.close()
    return logs

def save_mobility_test(user_id, test_data):
    """Save mobility test results."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO mobility_tests 
        (user_id, test_name, score, notes)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (
        user_id,
        test_data['test_name'],
        test_data['score'],
        test_data.get('notes', '')
    ))

    test_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    return test_id

def get_mobility_tests(user_id):
    """Get all mobility tests for a user."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM mobility_tests 
        WHERE user_id = %s 
        ORDER BY date DESC
    """, (user_id,))

    tests = cur.fetchall()
    cur.close()
    conn.close()
    return tests

def start_challenge(user_id, challenge_data):
    """Start a new challenge for a user."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO challenges 
        (user_id, challenge_name, end_date, progress)
        VALUES (%s, %s, CURRENT_TIMESTAMP + INTERVAL '%s days', %s)
        RETURNING id
    """, (
        user_id,
        challenge_data['name'],
        challenge_data['duration'],
        Json({'completed_tasks': [], 'current_day': 1})
    ))

    challenge_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    return challenge_id

def get_active_challenges(user_id):
    """Get all active challenges for a user."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM challenges 
        WHERE user_id = %s AND status = 'active'
        ORDER BY start_date DESC
    """, (user_id,))

    challenges = cur.fetchall()
    cur.close()
    conn.close()
    return challenges

def get_user_data(user_id):
    """Get all user data for dashboard display."""
    return {
        'assessments': get_assessments(user_id),
        'activities': get_activities(user_id),
        'stress_logs': get_stress_logs(user_id),
        'weight_logs': get_weight_logs(user_id),
        'mobility_tests': get_mobility_tests(user_id),
        'active_challenges': get_active_challenges(user_id)
    }