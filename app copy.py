from flask import Flask, request
import psycopg2
import os

app = Flask(__name__)

# Properly use environment variable
DATABASE_URL = os.environ['DATABASE_URL'].replace("postgres://", "postgresql://")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

@app.route('/submit', methods=['POST'])
def submit():
    input_text = request.form.get('text', '')
    word_count = len(input_text.split())

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO inputs (text, word_count) VALUES (%s, %s)", (input_text, word_count))
    conn.commit()
    cur.close()
    conn.close()

    return "Submitted! <a href='/history'>View History</a>"

@app.route('/history')
def history():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT text, word_count FROM inputs ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    history_html = "<h2>Input History</h2><ul>"
    for text, count in rows:
        history_html += f"<li>{text} ({count} words)</li>"
    history_html += "</ul>"
    return history_html

@app.route('/init_db')
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS inputs (
            id SERIAL PRIMARY KEY,
            text TEXT NOT NULL,
            word_count INTEGER NOT NULL
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()
    return "Database initialized!"
