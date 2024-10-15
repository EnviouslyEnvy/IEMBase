import sqlite3
import subprocess
import os
from flask import Flask, g, jsonify
from flask_apscheduler import APScheduler
from flask_cors import CORS

class Config:
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)
CORS(app, resources={r"/data/*": {"origins": "https://iem-base.vercel.app"}})
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

DATABASE = '/tmp/combined.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS combined (
                model TEXT,
                normalizedFloat REAL,
                toneFloat REAL,
                techFloat REAL,
                preferenceFloat REAL,
                maxComments TEXT,
                maxList TEXT,
                minComments TEXT,
                minList TEXT
            )
        ''')
        db.commit()

def generate_db():
    subprocess.run(["python", "get.py"], check=True)
    init_db()  # Initialize the database after running get.py

# Run 'generate_db' on startup
generate_db()

# Schedule 'generate_db' to run every week
scheduler.add_job(id='Refresh Database', func=generate_db, trigger='interval', hours=168)

@app.route('/')
def home():
    return "Welcome to the IEM Base API"

@app.route('/data/all')
def all():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM combined")
        results = cursor.fetchall()
        return jsonify([dict(row) for row in results])
    except sqlite3.Error as e:
        print('Database error:', str(e))
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        print('Unexpected error:', str(e))
        return jsonify({'error': 'An unexpected error occurred'}), 500
    finally:
        if cursor:
            cursor.close()

if __name__ == '__main__':
    with app.app_context():
        init_db()
    generate_db()
    app.run(debug=True)