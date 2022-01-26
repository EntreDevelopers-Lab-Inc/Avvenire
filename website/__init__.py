from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

# run it!
CORS(app, supports_credentials=True)
from website import routes

if __name__ == '__main__':
    app.run(threaded=True)
