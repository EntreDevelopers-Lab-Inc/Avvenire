from website import app
from flask import request
import time
import jwt

# make a constant for how long until timeout
TOKEN_SECONDS = 7200

# make a login cookie constant
LOGIN_COOKIE = 'token'


# make a function that creates tokens
def create_token(info_dict, exp=TOKEN_SECONDS):
    # add the expiration to the token
    info_dict['exp'] = time.time() + TOKEN_SECONDS

    # create the token
    token = jwt.encode(info_dict, app.config.get('JWT_SECRET_KEY'))

    return token


# make a function that checks the login
def check_login():
    token = request.cookies.get(LOGIN_COOKIE)

    if token:
        return token
    else:
        return None
