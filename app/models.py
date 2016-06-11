from app import db
from datetime import datetime
from sqlalchemy_utils import aggregated

class Sessions(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    title = db.Column(db.String, nullable=False)
    lastModified = db.Column(db.DateTime, default=datetime.utcnow)
    creator = db.Column(db.Integer)

    def json_view(self):
        return {"id": self.id, "title": self.title}

class Unranked(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    session = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String, nullable=False)
    avg_score = db.Column(db.Numeric(3,1), default=None)

    def json_view(self):
        return {"id": self.id, "session": self.session, "name": self.name, "score": str(self.avg_score)}

class Ranked(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    session = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    score = db.Column(db.Integer, nullable=False)

class Score(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    unranked_id = db.Column(db.Integer, db.ForeignKey('unranked.id'))
    unranked = db.relationship('Unranked',backref=db.backref('scores',lazy='dynamic'))
    user_id = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)

class Permission(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    granter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    granted_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    session = db.Column(db.String, nullable=False)

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

    def json_view(self):
        return {"id": self.id, "profile_pic": self.profile_pic, "name": self.name}

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

