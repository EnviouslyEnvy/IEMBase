import sqlite3
import subprocess
import os
from flask import Flask, g, jsonify
from flask_apscheduler import APScheduler
from flask_cors import CORS

class Config:
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)

# CORS(app) # For development
CORS(app, resources={r"/data/*": {"origins": [
    "https://iem-base.vercel.app", 
    "https://iemindex.com", 
    "https://www.iemindex.com",
    "https://api.iemindex.com"
]}}) # For deployment, updated to include new domain and API subdomain

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

def generate_db():
    # Run get.py to generate or update the database
    subprocess.run(["python", "get.py"], check=True)
    # For now, this is inefficient.
    # Get .py fetches and serves too much data,
    # But am planning a use for the unused and more comprehensive data later.

# Run 'generate_db' on startup
generate_db()

# Schedule 'generate_db' to run every week
scheduler.add_job(id='Refresh Database', func=generate_db, trigger='interval', hours=168)

# May want to make sure application works any deployment environment, make basedir for absolute pathing
# basedir = os.path.abspath(os.path.dirname(__file__))
# DATABASE = os.path.join(basedir, 'db', 'combined.db')
DATABASE = os.path.join('db', 'combined.db')

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

@app.route('/data/all')
def all():
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM combined")
        results = cursor.fetchall()
        return jsonify([dict(row) for row in results])
    except sqlite3.Error as e:
        print('Error:', e.args[0])
        return jsonify({'error': e.args[0]})
    finally:
        cursor.close()

if __name__ == '__main__':
    app.run(debug=True)