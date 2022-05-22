from website import db


# create a WL model
class WLModel(db.Model):
    __tablename__ = 'wls'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(128), nullable=False)
