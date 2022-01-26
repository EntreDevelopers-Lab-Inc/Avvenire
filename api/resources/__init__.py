from flask import request
from api import app
import json
import time
import jwt
from jwt.exceptions import ExpiredSignatureError

# make a constant for how long until timeout
TOKEN_MINUTES = 120


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
