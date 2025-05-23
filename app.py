from flask import Flask, request, render_template_string, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class TextEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    word_count = db.Column(db.Integer, nullable=False)

# Initialize database
with app.app_context():
    db.create_all()

# Read HTML file from root directory
with open("index.html", "r") as f:
    HTML_TEMPLATE = f.read()

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        text = request.form.get("text", "").strip()
        if text:
            word_count = len(text.split())
            entry = TextEntry(content=text, word_count=word_count)
            db.session.add(entry)
            db.session.commit()
            return redirect(url_for("home"))  # Refresh after submission

    # Fetch all entries and render HTML
    entries = TextEntry.query.order_by(TextEntry.id.desc()).all()
    return render_template_string(HTML_TEMPLATE, entries=entries)

if __name__ == "__main__":
    app.run(debug=True)