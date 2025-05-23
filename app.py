from flask import Flask, request, jsonify, abort
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.environ['DATABASE_URL'].replace("postgres://", "postgresql://")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

@app.route('/submit', methods=['POST'])
def submit():
    input_text = request.form.get('text', '').strip()
    if not input_text:
        return "Empty input not allowed", 400

    word_count = len(input_text.split())
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO inputs (text, word_count) VALUES (%s, %s)", (input_text, word_count))
    conn.commit()
    cur.close()
    conn.close()
    return "Submitted!", 200

@app.route('/history', methods=['GET'])
def history():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, text, word_count FROM inputs ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    # Return as JSON list of dicts
    data = [{"id": r[0], "text": r[1], "word_count": r[2]} for r in rows]
    return jsonify(data)

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
