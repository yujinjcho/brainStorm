from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_oauthlib.client import OAuth
from flask.ext.login import LoginManager

app = Flask(__name__, static_url_path='')
app.config.from_object('config')

lm = LoginManager()
lm.init_app(app)

db = SQLAlchemy(app)

oauth = OAuth(app)

facebook = oauth.remote_app(
    'facebook',
    consumer_key=app.config.get('FACEBOOK_APP_ID'),
    consumer_secret=app.config.get('FACEBOOK_APP_SECRET'),
    request_token_params={'scope': 'email'},
    base_url='https://graph.facebook.com',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    access_token_method='GET',
    authorize_url='https://www.facebook.com/dialog/oauth'
)


from app import views, models