import sqlite3
import os

DATABASE_PATH = 'polls.db'

def get_db():
    """Get a database connection"""
    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row  # Allows accessing columns by name
    return db

def init_db():
    """Initialize the database with tables if they don't exist"""
    db = get_db()
    cursor = db.cursor()
    
    # Create polls table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS polls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Create options table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS options (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            poll_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            FOREIGN KEY (poll_id) REFERENCES polls (id) ON DELETE CASCADE
        )
    ''')
    
    # Create votes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            poll_id INTEGER NOT NULL,
            option_id INTEGER NOT NULL,
            voted_at TEXT NOT NULL,
            FOREIGN KEY (poll_id) REFERENCES polls (id) ON DELETE CASCADE,
            FOREIGN KEY (option_id) REFERENCES options (id) ON DELETE CASCADE
        )
    ''')
    
    db.commit()
    db.close()
    
    print("Database initialized successfully!")

def reset_db():
    """Reset the database (delete all data)"""
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
    init_db()
    print("Database reset successfully!")

# Example usage to add sample data
def add_sample_data():
    """Add sample polls for testing"""
    db = get_db()
    cursor = db.cursor()
    
    # Sample poll 1
    cursor.execute(
        'INSERT INTO polls (question, created_at) VALUES (?, ?)',
        ('What is your favorite programming language?', '2026-01-01T10:00:00')
    )
    poll1_id = cursor.lastrowid
    
    languages = ['Python', 'JavaScript', 'Java', 'C++', 'Go']
    for lang in languages:
        cursor.execute(
            'INSERT INTO options (poll_id, text) VALUES (?, ?)',
            (poll1_id, lang)
        )
    
    # Sample poll 2
    cursor.execute(
        'INSERT INTO polls (question, created_at) VALUES (?, ?)',
        ('Which is the best framework for web development?', '2026-01-02T15:30:00')
    )
    poll2_id = cursor.lastrowid
    
    frameworks = ['React', 'Angular', 'Vue.js', 'Svelte', 'Django']
    for framework in frameworks:
        cursor.execute(
            'INSERT INTO options (poll_id, text) VALUES (?, ?)',
            (poll2_id, framework)
        )
    
    db.commit()
    db.close()
    print("Sample data added successfully!")

if __name__ == '__main__':
    init_db()
    add_sample_data()
