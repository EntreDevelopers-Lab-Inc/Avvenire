from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS

app = Flask(__name__)

app.config['SECRET_KEY'] = '45e2b67051014e2ba07df47f533c1f14'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///locovotiv.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# run it!
CORS(app, supports_credentials=True)
from api import routes
