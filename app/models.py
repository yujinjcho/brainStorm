from app import db
from datetime import datetime
from sqlalchemy_utils import aggregated
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import select, func

class User(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    auth_server_id = db.Column(db.String, default=None)
    created = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False
    )
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    profile_pic = db.Column(db.String, nullable=False)
    
    idea_session = db.relationship("IdeaSession", cascade='delete')
    ideas = db.relationship("Idea", cascade='delete')
    scores = db.relationship("Score", cascade='delete')
    permissions = db.relationship("Permission", cascade='delete')

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

class IdeaSession(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    idea = db.relationship("Idea", cascade='delete')
    permissions = db.relationship("Permission", cascade='delete')

    def json_view(self):
        return {"id": self.id, "name": self.name, "created": self.created, "creator": self.creator_id}

class Idea(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    idea_session_id = db.Column(db.Integer, db.ForeignKey('idea_session.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String, default=None)

    scores = db.relationship("Score", backref='idea', cascade='delete', lazy='dynamic')

    @hybrid_property
    def avg_score(self):
        scores_for_idea = [score.score for score in self.scores]
        if len(scores_for_idea) == 0:
            return 0
        return float(sum(scores_for_idea))/len(scores_for_idea)

    def json_view(self):
        score_format = '%.1f' % self.avg_score
        return {
            "id": self.id, 
            "session": self.idea_session_id,
            "creator_id" : self.creator_id,
            "name": self.name, 
            "score": score_format,
            "description": self.description
        }

class Score(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    score = db.Column(db.Numeric(2,1), nullable=False)
    idea_id = db.Column(db.Integer, db.ForeignKey('idea.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Permission(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    granted_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    idea_session_id = db.Column(db.Integer, db.ForeignKey('idea_session.id'), nullable=False)