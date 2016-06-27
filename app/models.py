from app import db
from datetime import datetime
from sqlalchemy_utils import aggregated

class IdeaSession(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, default='No Description')
    created = db.Column(db.DateTime, default=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def json_view(self):
        return {"id": self.id, "name": self.name, "created": self.created, "creator": self.creator_id}

class Idea(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    idea_session_id = db.Column(db.Integer, db.ForeignKey('idea_session.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    avg_score = db.Column(db.Numeric(3,1), default=None)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def json_view(self):
        return {"id": self.id, "session": self.idea_session_id, "name": self.name, "score": str(self.avg_score)}

class Score(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    idea_id = db.Column(db.Integer, db.ForeignKey('idea.id'), nullable=False)
    idea = db.relationship('Idea', backref=db.backref('scores',lazy='dynamic'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Permission(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    granter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    granted_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    idea_session_id = db.Column(db.Integer, db.ForeignKey('idea_session.id'), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    auth_server_id = db.Column(db.String, default=None)
    created = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False
    )
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    profile_pic = db.Column(db.String, nullable=False)
    idea_session = db.relationship("IdeaSession", backref='user', cascade="all, delete-orphan")
    ideas = db.relationship("Idea", backref='user', cascade="all, delete-orphan")
    scores = db.relationship("Score", backref='user', cascade="all, delete-orphan")

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

