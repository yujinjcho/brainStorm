
from flask import (
	render_template,
	request,
	redirect,
	jsonify,
	url_for,
	session,
	g
)
from flask_oauthlib.client import OAuthException
from flask.ext.login import (
    login_user, 
    logout_user, 
    login_required, 
    current_user,
)
from sqlalchemy import desc

from app import app, db, facebook, lm
from models import Sessions, Unranked, Ranked, User, Score

#rated_ideas = [{"session":"session 1","name":"yooo","score":8}]

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.before_request
def get_current_user():
    #Automatic logging in for testing
    user = User.query.filter(User.id == 1).first()
    login_user(user, remember=True)
    
    g.user = current_user

@app.route('/')
def index():
	if g.user.is_authenticated:
		groups_query = Sessions.query.filter(Sessions.creator == g.user.id)\
		.order_by(desc(Sessions.lastModified)).all()
	else:
		groups_query = Sessions.query.order_by(desc(Sessions.lastModified)).all()

	groups = [{
		"id": group.id, 
		"title": group.title
	} for group in groups_query]
	
	try:
		active_session = groups_query[0].id
	except:
		active_session = None

	group_set = set([int(group.id) for group in groups_query])
	scores = Score.query.filter(Score.user_id == g.user.id).all()
	scores_list = [score.unranked_id for score in scores]
	unrated_query = Unranked.query.filter(Unranked.session.in_(group_set)).all()
	
	unrated_ideas = [
		{"id": unrated.id, "session": unrated.session, "name": unrated.name}
		 for unrated in unrated_query
		 if unrated.id not in scores_list
	]
	rated_ideas = [
		{"id": unrated.id, "session": unrated.session, "name": unrated.name, "score": str(unrated.avg_score)}
		 for unrated in unrated_query
		 if unrated.id in scores_list
	]
	
	return render_template(
		'index.html', 
		sessions = groups, 
		unrated = unrated_ideas,
		rated = rated_ideas,
		active_session = active_session,
		user = g.user
	)

def json_view (self):
        return {"id": self.id, "title": self.title}

'''
@app.route('/sessions')
def get_group():
	groups_query = Sessions.query.all()	
	return jsonify(collection=[json_view(i) for i in groups_query])
'''

@app.route('/sessions', methods=['POST'])
def group_create():
	if request.method == 'POST':
		if current_user.is_authenticated:
			user = g.user.id
		else:
			user = None

		group = request.get_json()
		new_group = Sessions(title=group['title'], creator=user)
		db.session.add(new_group)
		db.session.flush()
		group = {"id": new_group.id, "title": new_group.title}
		db.session.commit()
		return _todo_response(group)

@app.route('/ideas')
def get_ideas():    
	if g.user.is_authenticated:
		groups_query = Sessions.query.filter(Sessions.creator == g.user.id)\
		.order_by(desc(Sessions.lastModified)).all()
	else:
		groups_query = Sessions.query.order_by(desc(Sessions.lastModified)).all()

	groups = [{
		"id": group.id, 
		"title": group.title
	} for group in groups_query]
	
	try:
		active_session = groups_query[0].id
	except:
		active_session = None

	group_set = set([int(group.id) for group in groups_query])
	scores = Score.query.filter(Score.user_id == g.user.id).all()
	scores_list = [score.unranked_id for score in scores]
	unrated_query = Unranked.query.filter(Unranked.session.in_(group_set)).all()
	
	rated_ideas = [
		{"id": unrated.id, "session": unrated.session, "name": unrated.name, "score": str(unrated.avg_score)}
		 for unrated in unrated_query
		 if unrated.id in scores_list
	]
	return jsonify(rated_ideas)

@app.route('/idea-model')
def refresh_model():    
    model_id = request.args.get('id')
    idea = Unranked.query.filter(Unranked.id==model_id).first()
    updated_idea = {
    	"id": idea.id,
    	"session": idea.session, 
    	"name": idea.name, 
    	"score": str(idea.avg_score)
    }
    return jsonify(updated_idea)

@app.route('/ideas', methods=['POST'])
def idea_create():
	idea = request.get_json()
	if 'score' in idea:
		new_score = Score(
			user_id = g.user.id,
			score = idea['score'],
			unranked_id = idea['id']
		)
		db.session.add(new_score)
		db.session.commit()
	else:
		new_idea = Unranked(
			session = idea['session'],
			name = idea['name']
		)
		db.session.add(new_idea)
		db.session.commit()
		idea['id'] = new_idea.id
	return _todo_response(idea)

@app.route('/scores', methods=['POST'])
def create_score():
	score = request.get_json()
	new_score = Score(
		unranked_id = score["unranked_id"],
		user_id = g.user.id,
		score = score["score"]
	)
	db.session.add(new_score)
	db.session.commit()
	score['id'] = new_score.id
	score['user_id'] = g.user.id
	updateAverage(score["unranked_id"])
	return _todo_response(score)	

def updateAverage(idea_id):
	idea = Unranked.query.filter_by(id=idea_id).first()
	scores_query = idea.scores.all()
	scores = [score.score for score in scores_query]
	idea.avg_score = sum(scores)/float(len(scores))
	db.session.commit()

def _todo_response(data):
    return jsonify(**data)

@app.route('/login')
def login():
    callback = url_for(
        'facebook_authorized',
        next=request.args.get('next')
            or request.referrer 
            or None,
        _external=True
    )
    return facebook.authorize(callback=callback)

@app.route('/login/fb_authorized')
def facebook_authorized():
    resp = facebook.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    if isinstance(resp, OAuthException):
        return 'Access denied: %s' % resp.message

    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get(
        '/me/?fields=email,name,id,picture.height(200).width(200)'
    )
    return set_user(me)

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')

def set_user(me):
	user = User.query.filter_by(
	    auth_server_id=me.data['id']
	).first()
	if user is None:
	    user = create_user(me)

	login_user(user, remember=True)
	return redirect(url_for('index'))

def create_user(me):  
    new_user = User(
        auth_server_id=me.data['id'],
        name=me.data['name'],
        email=me.data['email'],
        profile_pic=me.data['picture']['data']['url']
    )  

    db.session.add(new_user)
    db.session.commit()
    login_user(new_user, remember=True)
    return new_user

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/autocomplete/countries')
def autocomplete_countries():
	query = request.args.get('query')
	query_term = '%'+'%'.join(query.split('+'))+'%'
	users = User.query.filter(User.name.ilike(query_term)).all()
	users_list = [{"value": user.name, "id":user.id} for user in users]
	response = { "suggestions": users_list}
	return jsonify(response)

#TEST
@app.route('/query')
def query_test():    
    score = Score(unranked_id=30, user_id=2, score=0)
    db.session.add(score)
    db.session.commit()
    updateAverage(30)
    return 'done'

@app.route('/create_user')
def create_user():    
    new_user = User(
        auth_server_id=2,
        name='user2',
        email='email2',
        profile_pic='profilepic'
    )  

    db.session.add(new_user)
    db.session.commit()
    return 'done'


@app.route('/query2')
def query_test2():    
    idea = Unranked.query.filter_by(id=1).first()
    scores_query = idea.scores.all()
    list_scores = [each_score.score for each_score in scores_query]
    float_avg = sum(list_scores)/float(len(list_scores))
    return "%.1f" % float_avg
    
    