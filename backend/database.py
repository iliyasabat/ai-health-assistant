import sqlite3
import json
from datetime import datetime
import os
import hashlib

# Ensure the database directory exists
DB_DIR = "data"
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

DB_PATH = os.path.join(DB_DIR, "health_app.db")

def get_db_connection():
    """Create a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create users table (with authentication fields)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        height_cm REAL,
        weight_kg REAL,
        med_conditions TEXT,
        allergies TEXT,
        sleep_hours REAL,
        activity_level TEXT,
        diet_pref TEXT,
        gluten_free BOOLEAN,
        lactose_intol BOOLEAN,
        goal TEXT,
        target_weight REAL,
        target_duration INTEGER,
        bmi REAL,
        bmi_status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create favorite_recipes table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS favorite_recipes (
        recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        content TEXT,
        filters TEXT,
        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')

    # Create meal_logs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS meal_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        meal_type TEXT,
        description TEXT,
        calories INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')

    # Create weight_logs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS weight_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        weight REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')

    # Create water_logs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS water_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        ml INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')

    conn.commit()
    conn.close()

def register_user(email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)', (email, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, password_hash FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    if user and user['password_hash'] == hash_password(password):
        return user['user_id']
    return None

def get_user_id_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return user['user_id']
    return None

def save_user_profile(user_id, user_data):
    """Save or update user profile for a specific user_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    if user:
        cursor.execute('''
        UPDATE users SET
            age = ?, gender = ?, height_cm = ?, weight_kg = ?,
            med_conditions = ?, allergies = ?, sleep_hours = ?,
            activity_level = ?, diet_pref = ?, gluten_free = ?,
            lactose_intol = ?, goal = ?, target_weight = ?,
            target_duration = ?, bmi = ?, bmi_status = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?
        ''', (
            user_data['age'], user_data['gender'], user_data['height_cm'],
            user_data['weight_kg'], user_data['med_conditions'],
            user_data['allergies'], user_data['sleep_hours'],
            user_data['activity_level'], user_data['diet_pref'],
            user_data['gluten_free'], user_data['lactose_intol'],
            user_data['goal'], user_data['target_weight'],
            user_data['target_duration'], user_data['bmi'],
            user_data['bmi_status'], user_id
        ))
    else:
        cursor.execute('''
        UPDATE users SET
            age = ?, gender = ?, height_cm = ?, weight_kg = ?,
            med_conditions = ?, allergies = ?, sleep_hours = ?,
            activity_level = ?, diet_pref = ?, gluten_free = ?,
            lactose_intol = ?, goal = ?, target_weight = ?,
            target_duration = ?, bmi = ?, bmi_status = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?
        ''', (
            user_data['age'], user_data['gender'], user_data['height_cm'],
            user_data['weight_kg'], user_data['med_conditions'],
            user_data['allergies'], user_data['sleep_hours'],
            user_data['activity_level'], user_data['diet_pref'],
            user_data['gluten_free'], user_data['lactose_intol'],
            user_data['goal'], user_data['target_weight'],
            user_data['target_duration'], user_data['bmi'],
            user_data['bmi_status'], user_id
        ))
    conn.commit()
    conn.close()

def get_user_profile(user_id):
    """Get user profile for a specific user_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return dict(user)
    return None

def save_favorite_recipe(user_id, recipe_data):
    """Save a favorite recipe for a specific user_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO favorite_recipes (user_id, title, content, filters)
    VALUES (?, ?, ?, ?)
    ''', (
        user_id,
        recipe_data['title'],
        recipe_data['content'],
        json.dumps(recipe_data['filters'])
    ))
    conn.commit()
    conn.close()

def get_favorite_recipes(user_id):
    """Get all favorite recipes for a specific user_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM favorite_recipes WHERE user_id = ? ORDER BY date_added DESC', (user_id,))
    recipes = cursor.fetchall()
    conn.close()
    return [dict(recipe) for recipe in recipes]

def delete_favorite_recipe(user_id, recipe_id):
    """Delete a favorite recipe for a specific user_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM favorite_recipes WHERE recipe_id = ? AND user_id = ?', (recipe_id, user_id))
    conn.commit()
    conn.close()

def save_meal_log(user_id, meal_data):
    """Save a meal log entry for a specific user_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO meal_logs (user_id, date, meal_type, description, calories)
    VALUES (?, ?, ?, ?, ?)
    ''', (
        user_id,
        meal_data['date'],
        meal_data['meal_type'],
        meal_data['description'],
        meal_data['calories']
    ))
    conn.commit()
    conn.close()

def get_meal_logs(user_id):
    """Get all meal logs for a specific user_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM meal_logs WHERE user_id = ? ORDER BY date DESC', (user_id,))
    logs = cursor.fetchall()
    conn.close()
    return [dict(log) for log in logs]

def save_weight_log(user_id, weight_data):
    """Save a weight log entry for a specific user_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO weight_logs (user_id, date, weight)
    VALUES (?, ?, ?)
    ''', (user_id, weight_data['date'], weight_data['weight']))
    conn.commit()
    conn.close()

def get_weight_logs(user_id):
    """Get all weight logs for a specific user_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM weight_logs WHERE user_id = ? ORDER BY date DESC', (user_id,))
    logs = cursor.fetchall()
    conn.close()
    return [dict(log) for log in logs]

def save_water_log(user_id, water_data):
    """Save a water log entry for a specific user_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO water_logs (user_id, date, ml)
    VALUES (?, ?, ?)
    ''', (user_id, water_data['date'], water_data['ml']))
    conn.commit()
    conn.close()

def get_water_logs(user_id):
    """Get all water logs for a specific user_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM water_logs WHERE user_id = ? ORDER BY date DESC', (user_id,))
    logs = cursor.fetchall()
    conn.close()
    return [dict(log) for log in logs]

# Initialize the database when the module is imported
init_db() 