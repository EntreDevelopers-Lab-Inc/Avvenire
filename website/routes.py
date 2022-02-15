from website import app
from website.tools import check_login, create_token, LOGIN_COOKIE
from flask import render_template, request, Flask, g, send_from_directory, abort, jsonify, make_response
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, set_access_cookies, get_jwt, verify_jwt_in_request
from eth_account.messages import defunct_hash_message
from web3.auto import w3
import time


@app.route('/home')
@app.route('/')
def home():
    token = check_login()

    # find a way to only show connect wallet if they are connected
    return render_template('home.html', logged_in=bool(token))


@app.route('/connect-wallet')
def connect_wallet():
    return render_template('connect-wallet.html')


# this just gets rid of the connect wallet page, not actually using the backend for contract interaction (can just pass the selected account's address directly if necessary)
@app.route('/login', methods=['POST'])
def login():
    public_address = request.json[0]

    if public_address:
        access_token = create_token({'identity': public_address})
    else:
        access_token = None

    resp = jsonify({'login': True, 'token': access_token})

    return resp, 200


# allow logout
@app.route('/logout', methods=['GET'])
def logout():
    # make a response objcet
    resp = make_response(render_template(
        'home.html', logged_in=False, dark_nav=True))

    # delete the cookie
    resp.delete_cookie(LOGIN_COOKIE)

    # sent the user to the login screen
    return resp


# use @jwt-required for mint function
# can also get the identity with get_jwt_identity()
