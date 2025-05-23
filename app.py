from flask import Flask, request, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class TextEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    word_count = db.Column(db.Integer, nullable=False)

@app.route("/", methods=["GET"])
def home():
    # Serve the index.html file from the root directory
    return send_file("index.html")

@app.route("/", methods=["POST"])
def process_text():
    data = request.get_json()
    text = data.get("text", "")
    word_count = len(text.split())

    entry = TextEntry(content=text, word_count=word_count)
    db.session.add(entry)
    db.session.commit()

    return jsonify({"word_count": word_count})

# ✅ Wrap db.create_all() in an app context
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
