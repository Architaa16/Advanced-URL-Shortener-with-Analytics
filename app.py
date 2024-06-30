from flask import Flask, request, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
import string
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_url = db.Column(db.String(6), unique=True, nullable=False)
    visits = db.Column(db.Integer, default=0)

def generate_short_url():
    characters = string.ascii_letters + string.digits
    while True:
        short_url = ''.join(random.choices(characters, k=6))
        if not URL.query.filter_by(short_url=short_url).first():
            return short_url

@app.route('/', methods=['GET', 'POST'])
def index():
    db.create_all()  # Create tables if they don't exist
    if request.method == 'POST':
        original_url = request.form['original_url']
        short_url = generate_short_url()
        new_url = URL(original_url=original_url, short_url=short_url)
        db.session.add(new_url)
        db.session.commit()
        return f'Shortened URL is: {request.host_url}{short_url}'
    return render_template('index.html')

@app.route('/<short_url>')
def redirect_to_url(short_url):
    url = URL.query.filter_by(short_url=short_url).first_or_404()
    url.visits += 1
    db.session.commit()
    return redirect(url.original_url)

@app.route('/analytics')
def analytics():
    urls = URL.query.all()
    return render_template('analytics.html', urls=urls)

if __name__ == '__main__':
    app.run(debug=True)
