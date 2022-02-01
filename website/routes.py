from website import app
from flask import render_template, request, Flask, g, send_from_directory, abort, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, set_access_cookies
from eth_account.messages import defunct_hash_message
from web3.auto import w3
import time


@app.route('/home')
@app.route('/')
def home():
    # find a way to only show connect wallet if they are connected
    return render_template('home.html')


@app.route('/connect-wallet')
def connect_wallet():
    return render_template('connect-wallet.html')


@app.route('/login', methods=['POST'])
def login():

    print("[+] creating session")

    print("info: " + (str(request.json)))

    public_address = request.json[0]
    signature = request.json[1]

    test_string = "Avvenire"

    rightnow = int(time.time())
    sortanow = rightnow - rightnow % 600

    original_message = 'Signing in to {} at {}'.format(test_string, sortanow)
    message_hash = defunct_hash_message(text=original_message)
    signer = w3.eth.account.recoverHash(message_hash, signature=signature)

    if signer == public_address:
        print("[+] this is fine " + str(signer))
        # account.nonce = account.generate_nonce()
        # db.session.commit()
    else:
        abort(401, 'could not authenticate signature')

    print("[+] OMG looks good")

    access_token = create_access_token(identity=public_address)

    resp = jsonify({'login': True})
    set_access_cookies(resp, access_token)
    return resp, 200


# use @jwt-required for mint function
