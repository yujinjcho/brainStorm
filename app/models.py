from app import db

class Sessions(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    title = db.Column(db.String, nullable=False)

class Unranked(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    session = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)

class Ranked(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    session = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    score = db.Column(db.Integer, nullable=False)