from flask_restful import Resource
from api.resources import load_json
from api.models import db, UserModel, validate_user
from api import bcrypt, app
from datetime import datetime as dt, timedelta
import jwt


# make a constant for how long until timeout
TOKEN_MINUTES = 120

# create a resource for user addition


class UserManagementResource(Resource):
    # create users
    def post(self):
        json_data = load_json()

        # get the email and password
        try:
            email = json_data['email']
            password = json_data['password']
            confirmed_password = json_data['confirmed_password']
        except KeyError:
            return {'message': 'request must include email, password, and confirmed_password'}, 422

        # check if the user exists
        test_user = UserModel.query.filter_by(email=email).first()
        if test_user:
            return {'message': f"There is already an account associated with {email}."}, 403

        # check if the passwords match
        if password != confirmed_password:
            return {'message': 'Passwords do not match.'}, 409

        # hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # create a user and add it to the database
        new_user = UserModel(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return {'status': 'success'}, 201

    # change user attributes (just the password for now)
    def put(self):
        json_data = load_json()

        # get relevant data
        try:
            email = json_data['email']
            old_password = json_data['old_password']
            new_password = json_data['new_password']
        except KeyError:
            return {'message', 'email, old_password, and new_password are required'}, 422

        validated, user, code = validate_user(email, old_password)

        if not validated:
            return user, code

        # change the password
        user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()

        return {'status': 'success'}, 201

    # create a function that deletes users (should be available to everyone)

    def delete(self):
        json_data = load_json()

        # get the data
        try:
            email = json_data['email']
            password = json_data['password']
        except KeyError:
            return {'message': 'email and password are required'}, 422

        validated, user, code = validate_user(email, password)

        if not validated:
            return user, code

        # delete the user
        db.session.delete(user)
        db.session.commit()

        return {'status': 'success', 'message': f"Deleted account attached to {user.email}"}, 201


# create a class for login verification
class LoginResource(Resource):
    def post(self):
        data = load_json()

        # get the data
        try:
            email = data['email']
            password = data['password']
        except KeyError:
            return {'message': 'email and password are required'}, 422

        # choose whether the email and password match or not
        validated, user, code = validate_user(email, password)

        if validated:
            give_token = True
            output = {'status': 'success', 'loggedIn': True}
        else:
            give_token = False
            user['loggedIn'] = False
            output = user

        # add a token to the output (if applicable)
        if give_token:
            token = jwt.encode({'id': user.id, 'exp': dt.utcnow(
            ) + timedelta(minutes=TOKEN_MINUTES)}, app.config.get('SECRET_KEY'))
            output['token'] = token.decode('UTF-8')

        return output, code

'''
NOTES
- see this link for token info: https://geekflare.com/securing-flask-api-with-jwt/

token = jwt.encode({'id': 7, 'exp': dt.utcnow() + timedelta(minutes=10)}, 'c0115a8363cdd98b3c822c1adba5a7c9')
'''
