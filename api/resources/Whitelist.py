from api.models import db, WhitelistedAccountModel
from api.resources import load_json, check_keys
from flask_restful import Resource


# make a way to add people to the whitelist
class WhitelistResource(Resource):
    # check if an address is on the whitelist
    def get(self):
        required_keys = {'eth_address'}

        if not check_keys(request.headers, required_keys):
            return {'message': f"must include {required_keys}"}

        # check the database for the address
        whitelist_spot = WhitelistedAccountModel.query.filter_by(
            address=request.headers['eth_address']).first()

        # if there is no whitelist spot, return such
        if not whitelist_spot:
            return {'status': 'success', 'message': 'This address has not requested to join the whitelist.'}, 201
        # if there is a whitelist spot, return such depending on verification status
        elif whitelist_spot.verified is True:
            return {'status': 'success', 'message': 'This address has been approved for the whitelist.'}, 201
        elif whitelist_spot.verified is False:
            return {'status': 'success', 'message': 'This address has requested to join the whitelist, but has not yet been approved.'}

    # add to the whitelist
    def post(self):
        json_data, code = self.safe_load_json()

        # if the code is greater than 200, return the information
        if code > 200:
            return json_data, code

        # check if there is an account with the discord username
        if WhitelistedAccountModel.filter_by(discord_username=json_data['discord_username']).first():
            return {'message': f"{json_data['discord_username']} has already requested a whitelist spot"}, 409

        # check if there is an account with the eth address
        if WhitelistedAccountModel.filter_by(address=json_data['eth_address']).first():
            return {'message': f"{json_data['eth_address']} has already requested a whitelist spot"}, 409

        # make a new account model
        whitelist_spot = WhitelistedAccountModel(
            discord_username=json_data['discord_username'], address=json_data['eth_address'], pin=json_data['pin'])
        db.session.add(whitelist_spot)
        db.session.commit()

        return {'status': 'success'}, 201

    # delete an account from the whitelist (need the discord username, eth address, and pin --> max security to keep people from trying to hack into whitelist)
    def delete(self):
        # get the json
        json_data, code = self.safe_load_json()

        # if the code if greater than 200, return it
        if code > 200:
            return json_data, code

        # check if there is an account with the username, address, and pin
        whitelist_spot = WhitelistedAccountModel.query.filter_by(
            discord_username=json_data['discord_username'], address=json_data['eth_address'], pin=json_data['pin']).first()

        # if there is no whitelist spot, return such
        if not whitelist_spot:
            return {'message': 'No whitelist spot found.'}, 404

        # else, delete the whitelist spot
        db.session.delete(whitelist_spot)
        db.session.commit()

        return {'status': 'success'}, 201

    def safe_load_json(self):
        # get the json
        json_data = load_json()

        # check the keys for the discord username, address, and pin
        required_keys = {'discord_username', 'pin'}

        if not check_keys(json_data, required_keys):
            return {'message': f"must include: {required_keys}"}, 422

        # add the eth address based on the web3 framework

        # if it gets here, return status code 200 for success
        return json_data, 200
