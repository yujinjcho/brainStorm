# Synopsis
Tool to collaboratively create and rank ideas.

# Installation
Clone the repository.

`git clone https://github.com/yujinjcho/brainStorm.git`

Create a virtual environment. I'm using virtualenvwrapper in this case.

`mkvirtualenv idea_storm`

Install dependencies.

`pip install -r requirements.txt`

# Config
Create `config.py` and add to root project folder and fill in config variables below. Create new Facebook project to get IDs and SECRETs. Requires a database URI as well.

```
DEBUG = True
SECRET_KEY = 'SECRET_KEY'
SQLALCHEMY_DATABASE_URI = "SQLALCHEMY_DATABASE_URI"
FACEBOOK_APP_ID = 'FACEBOOK_APP_ID'
FACEBOOK_APP_SECRET = 'FACEBOOK_APP_SECRET'
SENTRY_DSN='SENTRY_DSN'
```

# Run Locally
Initialize database before running app.
```
python
>>>from app import db
>>>db.create_all()
>>>quit()

python run.py
```

# License
This project is licensed under the MIT License - see the [license.txt](https://github.com/yujinjcho/brainStorm/blob/master/LICENSE.TXT) file for details
