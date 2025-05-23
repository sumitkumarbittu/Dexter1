from flask import Flask, request, render_template_string
import psycopg2
import os

app = Flask(__name__)

# Connect to PostgreSQL (Render will set DATABASE_URL)
def get_db_connection():
    conn = psycopg2.connect(os.environ['postgresql://sql1_xuo9_user:aBz6U5caB8X0DoU6CbOPeootTNat6Sm7@dpg-d0o4f8umcj7s73e49320-a/sql1_xuo9'], sslmode='require')
    return conn

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
