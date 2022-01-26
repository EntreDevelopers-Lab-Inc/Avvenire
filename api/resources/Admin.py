from flask_restful import Resource
from api.resources import load_json, validate_admin_token, load_header_token, TOKEN_MINUTES
from api.models import db, UserModel, validate_admin
from api import app
from datetime import datetime as dt, timedelta
import jwt

# create a class for admins to get all the user data


class AdminUserManagementResource(Resource):
    # create a post method to get all the users
    def get(self):
        # get the admin_data and authenticate the admin
        token = load_header_token()

        # validate the admin
        message, error_code = validate_admin_token(token)
        if message:
            return message, error_code

        # get the data from all the users
        users = [{'email': user.email} for user in UserModel.query.all()]

        return {'users': users}, 201

    # create a method to delete users from the admin page (without a password)
    def delete(self):
        data = load_json()

        # validate the admin
        message, error_code = validate_admin_token(data['token'])
        if message:
            return message, error_code

        # find the user to delete via email
        user_email = data['user_email']
        user = UserModel.query.filter_by(email=user_email).first()

        # if no user, return so
        if not user:
            return {'message': f"no account associated with {user_email}"}, 404

        # else delete the user
        db.session.delete(user)
        db.session.commit()

        return {'status': 'success', 'message': f"Deleted {user_email}"}, 201


# create a class to log in admins
class AdminLoginResource(Resource):
    def post(self):
        data = load_json()

        # validate the admin
        if not validate_admin(data['email'], data['password']):
            return {'message': 'You are not allowed to access this resource.'}, 403

        # get a token and give it to the admin
        token = jwt.encode({'admin_access': True, 'exp': dt.utcnow() + timedelta(minutes=TOKEN_MINUTES)}, app.config['SECRET_KEY']).decode('UTF-8')

        return {'status': 'success', 'token': token}
