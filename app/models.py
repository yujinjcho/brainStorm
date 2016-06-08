from app import db
from datetime import datetime

class Sessions(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    title = db.Column(db.String, nullable=False)
    lastModified = db.Column(db.DateTime, default=datetime.utcnow)

class Unranked(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    session = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)

class Ranked(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    session = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    score = db.Column(db.Integer, nullable=False)