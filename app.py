from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# DATABASE_URL from Render environment variable
DATABASE_URL = os.environ['DATABASE_URL'].replace("postgres://", "postgresql://")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

#test database
@app.route('/test_db')
def test_db():
    try:
        conn = get_db_connection()
        conn.close()
        return "Database connection OK"
    except Exception as e:
        return f"DB connection error: {e}", 500


# Initialize the DB table with user and timestamp
@app.route('/init_db')
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS inputs (
            id SERIAL PRIMARY KEY,
            name TEXT DEFAULT 'unknown',
            text TEXT NOT NULL,
            word_count INTEGER NOT NULL,
            timestamp TIMESTAMPTZ DEFAULT NOW()
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()
    return "Database initialized!"



# Submit a new entry
@app.route('/submit', methods=['POST'])
def submit():
    input_text = request.form.get('text', '').strip()
    name = request.form.get('name', 'Unknown').strip()
    if not input_text:
        return "Empty input not allowed", 400

    word_count = len(input_text.split())
    timestamp = datetime.utcnow()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO inputs (name, text, word_count, timestamp)
        VALUES (%s, %s, %s, %s)
    """, (name or 'Unknown', input_text, word_count, timestamp))
    conn.commit()
    cur.close()
    conn.close()

    return "Submitted!", 200

# Get all entries
@app.route('/history', methods=['GET'])
def history():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, text, word_count, timestamp FROM inputs ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    data = [{
        "id": r[0],
        "name": r[1],
        "text": r[2],
        "word_count": r[3],
        "timestamp": r[4].isoformat()
    } for r in rows]
    return jsonify(data)

# Delete an entry by ID
@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM inputs WHERE id = %s RETURNING id", (item_id,))
    deleted = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if deleted:
        return "Deleted", 200
    else:
        return abort(404, description="Item not found")


#clear database
@app.route('/clear_db')
def clear_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM inputs;")  # use TRUNCATE if you want to reset auto-increment ID
    conn.commit()
    cur.close()
    conn.close()
    return "All data cleared!"


# Danger: Permanently delete the entire table
@app.route('/drop_table', methods=['GET', 'POST'])
def drop_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS inputs;")
    conn.commit()
    cur.close()
    conn.close()
    return "Table 'inputs' dropped successfully!", 200
