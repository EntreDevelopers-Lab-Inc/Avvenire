from api import db
from api import bcrypt
from api.admin_config import ADMIN_PROFILE


# create a user model
class UserModel(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(320), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

    creation_date = db.Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp())


# create a whitelist model
class WhitelistedAccountModel(db.Model):
    __tablename__ = 'whitelisted_accounts'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(42), nullable=False,
                        unique=True)  # limit set on eth addresses

    # limit on discord username length + 5 for number at end
    discord_username = db.Column(db.String(37), unique=True, nullable=False)

    # 4 digit pin for deleting account (no need for complex usernames and passwords, this is just a whitelist after all)
    pin = db.Column(db.String(4), nullable=False)

    # verification that only the admin can set
    verified = db.Column(db.Boolean, default=False)

    # keep track of when the whitelist user was created
    creation_date = db.Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp())


# create a function to validate users
def validate_user(email, password):
    # get the user
    user = UserModel.query.filter_by(email=email).first()

    if not user:
        return False, {'message': f"no account associated with {email}"}, 404

    # check if passwords match
    if not bcrypt.check_password_hash(user.password, password):
        return False, {'message': f"incorrect password for {email}"}, 401

    return True, user, 201


def validate_admin(email, password):
    print(ADMIN_PROFILE['email'] + ' ' + ADMIN_PROFILE['password'])
    if email != ADMIN_PROFILE['email']:
        return False
    elif password != ADMIN_PROFILE['password']:
        return False
    else:
        return True


# create a function to handle datetimes
def check_dt(value):
    if type(value) is dt:
        value = value.strftime('%s')

    return value


def object_as_dict(obj):
    obj_dict = {c.key: getattr(obj, c.key)
                for c in db.inspect(obj).mapper.column_attrs}

    # format datetimes
    obj_dict = {key: check_dt(value) for key, value in obj_dict.items()}
    return obj_dict

# create a function that set object attributes to a dict


def set_object_to_dict(obj, obj_dict):
    for key, value in obj_dict.items():
        db.setattr(obj, key, value)
