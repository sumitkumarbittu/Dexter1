from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class TextEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    word_count = db.Column(db.Integer, nullable=False)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        text = request.form["text"]
        word_count = len(text.split())
        entry = TextEntry(content=text, word_count=word_count)
        db.session.add(entry)
        db.session.commit()
    entries = TextEntry.query.all()
    return render_template("index.html", entries=entries)

# ✅ Wrap `db.create_all()` in an application context
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
