from app import db
from datetime import datetime

class Sessions(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    title = db.Column(db.String, nullable=False)
    lastModified = db.Column(db.DateTime, default=datetime.utcnow)
    creator = db.Column(db.Integer)

class Unranked(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    session = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)

class Ranked(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    session = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    score = db.Column(db.Integer, nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    auth_server_id = db.Column(db.String, default=None)
    created = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False
    )
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    profile_pic = db.Column(db.String, nullable=False)
    

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3
