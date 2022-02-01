from website import app
from flask import render_template


@app.route('/home')
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/connect-wallet')
def connect_wallet():
    return render_template('connect-wallet.html')
