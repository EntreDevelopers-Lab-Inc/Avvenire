from website import app, db
from website.models import WLModel
from flask import render_template


@app.route('/home')
@app.route('/')
def home():
    # find a way to only show connect wallet if they are connected
    return render_template('home.html')


@app.route('/mint')
def mint():
    return render_template('mint.html')


# a route to add WL
@app.route('/add_wl/<address>/<amount>')
def add_wl(address, amount):
    # get the address
    test_addr = WLModel.query.filter_by(address=address).first()

    # check if the address exists
    if not test_addr:
        # if the address does not exist, add it
        new_address = WLModel(address=address, limit=amount)
        db.session.add(new_address)
    else:
        # just change it
        test_addr.limit = amount

    # commit the changes
    db.session.commit()

    return {'added': True, 'limit': amount}


# a route to test if a wl exists
@app.route('/wl_exists/<address>')
def wl_exists(address):
    # get the address
    test_addr = WLModel.query.filter_by(address=address).first()

    # check if the address exists
    if test_addr:
        return {'exists': True, 'limit': test_addr.limit}
    else:
        return {'exists': False}
