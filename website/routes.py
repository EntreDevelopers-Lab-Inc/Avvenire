from website import app
from flask import render_template


@app.route('/home')
@app.route('/')
def home():
    return render_template('index.html')
