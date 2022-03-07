from flask import request
from api import app
import json
import time
import jwt
from jwt.exceptions import ExpiredSignatureError

# make a constant for how long until timeout
TOKEN_MINUTES = 120

# add some excluded keys
EXCLUDED_KEYS = {'id'}


def load_json():
    try:
        json_data = json.loads(request.get_json(force=True))
    except TypeError:
        json_data = request.get_json(force=True)

    return json_data


def load_header_token():
    token = request.headers.get('token')

    return token


def validate_admin_token(token):
    try:
        privileges = jwt.decode(token, app.config.get('SECRET_KEY'))
    except ExpiredSignatureError:
        return {'message': 'Token is expired'}, 401

    try:
        access = privileges['admin_access']
        exp = privileges['exp']
    except KeyError:
        return {'message': 'invalid token', 'contains': privileges}, 401

    # check the info in the token
    if access is False:
        return {'message': 'You are not allowed to access this resource.'}, 403
    elif exp < time.time():
        return {'message': 'Token is expired'}, 401
    else:
        return None, 201


def validate_user_token(token):
    try:
        privileges = jwt.decode(token, app.config.get('SECRET_KEY'))
    except ExpiredSignatureError:
        return {'message': 'Token is expired'}, 401

    try:
        exp = privileges['exp']
    except KeyError:
        return {'message': 'invalid token', 'contains': privileges}, 401

    if exp < time.time():
        return {'message': 'Token is expired'}, 401

    # if it gets here the token is valid --> get the user data
    return privileges, 201


# make a function to check if keys exist
def check_keys(given_keys, required_keys, debug=False):
    # output what was received if there is a debug
    if debug:
        print(f"given_keys: {given_keys}")
        print(f"required_keys: {required_keys}")

    # clean the keys
    required_keys -= EXCLUDED_KEYS

    if all(key in given_keys for key in required_keys):
        return True
    else:
        return False
