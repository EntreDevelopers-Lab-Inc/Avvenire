from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import random
import string

app = Flask(__name__)

# Setup the Flask-JWT-Extended extension
# log2(26^22) ~= 100 (pull at least 100 bits of entropy)
app.config['JWT_SECRET_KEY'] = ''.join(
    random.choice(string.ascii_lowercase) for i in range(22))
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = True
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
jwt = JWTManager(app)

# run it!
CORS(app, supports_credentials=True)
from website import routes

if __name__ == '__main__':
    app.run(threaded=True)
