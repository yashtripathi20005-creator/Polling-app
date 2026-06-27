from flask import Flask, render_template, request, redirect, url_for, flash
from models import Poll, Vote
from database import init_db, get_db
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# Initialize database
init_db()

@app.route('/')
def index():
    """Home page showing all polls"""
    db = get_db()
    cursor = db.cursor()
    
    # Get all polls with vote counts
    cursor.execute('''
        SELECT p.*, COUNT(v.id) as vote_count 
        FROM polls p
        LEFT JOIN votes v ON p.id = v.poll_id
        GROUP BY p.id
        ORDER BY p.created_at DESC
    ''')
    polls = cursor.fetchall()
    db.close()
    
    return render_template('index.html', polls=polls)

@app.route('/poll/<int:poll_id>')
def view_poll(poll_id):
    """View a specific poll and vote"""
    db = get_db()
    cursor = db.cursor()
    
    # Get poll details
    cursor.execute('SELECT * FROM polls WHERE id = ?', (poll_id,))
    poll = cursor.fetchone()
    
    if not poll:
        db.close()
        flash('Poll not found!', 'error')
        return redirect(url_for('index'))
    
    # Get options for this poll
    cursor.execute('SELECT * FROM options WHERE poll_id = ?', (poll_id,))
    options = cursor.fetchall()
    
    # Get vote counts for each option
    option_votes = []
    for option in options:
        cursor.execute('SELECT COUNT(*) FROM votes WHERE option_id = ?', (option['id'],))
        count = cursor.fetchone()[0]
        option_votes.append({
            'id': option['id'],
            'text': option['text'],
            'votes': count
        })
    
    db.close()
    return render_template('poll.html', poll=poll, options=option_votes)

@app.route('/vote/<int:poll_id>', methods=['POST'])
def vote(poll_id):
    """Submit a vote"""
    option_id = request.form.get('option')
    
    if not option_id:
        flash('Please select an option!', 'error')
        return redirect(url_for('view_poll', poll_id=poll_id))
    
    db = get_db()
    cursor = db.cursor()
    
    # Check if poll exists
    cursor.execute('SELECT * FROM polls WHERE id = ?', (poll_id,))
    poll = cursor.fetchone()
    
    if not poll:
        db.close()
        flash('Poll not found!', 'error')
        return redirect(url_for('index'))
    
    # Check if option belongs to this poll
    cursor.execute('SELECT * FROM options WHERE id = ? AND poll_id = ?', (option_id, poll_id))
    option = cursor.fetchone()
    
    if not option:
        db.close()
        flash('Invalid option!', 'error')
        return redirect(url_for('view_poll', poll_id=poll_id))
    
    # Record the vote
    cursor.execute(
        'INSERT INTO votes (poll_id, option_id, voted_at) VALUES (?, ?, ?)',
        (poll_id, option_id, datetime.now().isoformat())
    )
    db.commit()
    db.close()
    
    flash('Vote recorded successfully!', 'success')
    return redirect(url_for('results', poll_id=poll_id))

@app.route('/results/<int:poll_id>')
def results(poll_id):
    """Show poll results"""
    db = get_db()
    cursor = db.cursor()
    
    # Get poll details
    cursor.execute('SELECT * FROM polls WHERE id = ?', (poll_id,))
    poll = cursor.fetchone()
    
    if not poll:
        db.close()
        flash('Poll not found!', 'error')
        return redirect(url_for('index'))
    
    # Get options with vote counts
    cursor.execute('''
        SELECT o.*, COUNT(v.id) as vote_count 
        FROM options o
        LEFT JOIN votes v ON o.id = v.option_id
        WHERE o.poll_id = ?
        GROUP BY o.id
        ORDER BY vote_count DESC
    ''', (poll_id,))
    options = cursor.fetchall()
    
    # Calculate total votes
    total_votes = sum(opt['vote_count'] for opt in options)
    
    db.close()
    return render_template('results.html', poll=poll, options=options, total_votes=total_votes)

@app.route('/create', methods=['GET', 'POST'])
def create_poll():
    """Create a new poll"""
    if request.method == 'POST':
        question = request.form.get('question')
        options_text = request.form.getlist('option')
        
        # Validate input
        if not question:
            flash('Please enter a question!', 'error')
            return render_template('create.html')
        
        # Filter out empty options
        options_text = [opt.strip() for opt in options_text if opt.strip()]
        
        if len(options_text) < 2:
            flash('Please provide at least 2 options!', 'error')
            return render_template('create.html')
        
        db = get_db()
        cursor = db.cursor()
        
        # Insert poll
        cursor.execute(
            'INSERT INTO polls (question, created_at) VALUES (?, ?)',
            (question, datetime.now().isoformat())
        )
        poll_id = cursor.lastrowid
        
        # Insert options
        for option_text in options_text:
            cursor.execute(
                'INSERT INTO options (poll_id, text) VALUES (?, ?)',
                (poll_id, option_text)
            )
        
        db.commit()
        db.close()
        
        flash('Poll created successfully!', 'success')
        return redirect(url_for('view_poll', poll_id=poll_id))
    
    return render_template('create.html')

@app.route('/delete/<int:poll_id>', methods=['POST'])
def delete_poll(poll_id):
    """Delete a poll and all associated data"""
    db = get_db()
    cursor = db.cursor()
    
    # Delete votes first (foreign key constraint)
    cursor.execute('DELETE FROM votes WHERE poll_id = ?', (poll_id,))
    cursor.execute('DELETE FROM options WHERE poll_id = ?', (poll_id,))
    cursor.execute('DELETE FROM polls WHERE id = ?', (poll_id,))
    
    db.commit()
    db.close()
    
    flash('Poll deleted successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
