
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
from models import (
	Sessions,
	Unranked, 
	Ranked, 
	User, 
	Score, 
	Permission
)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.before_request
def get_current_user():
    ########################################
	#FOR TESTING PURPOSES
    #user = User.query.filter(User.id == 1).first()
    #login_user(user, remember=True)
    ########################################
    
    g.user = current_user

def get_sessions(active_user):
	sessions_q = Sessions.query.filter(
		Sessions.creator == active_user
	).order_by(Sessions.lastModified).all()

	if not sessions_q:
		active_session = None
	else:
		active_session = sessions_q[-1].id

	groups = [s.json_view() for s in sessions_q]
	group_ids = [int(s.id) for s in sessions_q]
	return active_session, group_ids, groups

def get_ideas(groups, active_user):
	if active_user is None:
		return [], []

	scores = Score.query.filter(Score.user_id == g.user.id).all()
	scored_ideas = [score.unranked_id for score in scores]
	unrated_q = Unranked.query.filter(Unranked.session.in_(set(groups))).all()
	
	unrated_ideas = [
		idea.json_view() for idea in unrated_q 
		if idea.id not in scored_ideas
	]
	rated_ideas = [
		idea.json_view() for idea in unrated_q 
		if idea.id in scored_ideas
	]

	return unrated_ideas, rated_ideas

def get_permissions(active_user):
	if active_user is None:
		return []

	permissions_query = Permission.query.filter(Permission.granter_id == g.user.id).all()
	permissions = [
		{'id': permission.id,
		 'granted_id': permission.granted_id, 
		 "session": permission.session}
		for permission in permissions_query
	]
	return permissions

def get_users(permissions):
	users_access = set([p['granted_id'] for p in permissions])
	users_query = User.query.filter(User.id.in_(users_access)).all()
	users = [u.json_view() for u in users_query]
	return users

@app.route('/')
def index():
	if not g.user.is_authenticated:
		active_user = None
	else:
		active_user = g.user

	active_session, group_ids, groups = get_sessions(active_user)
	unrated_ideas, rated_ideas = get_ideas(group_ids, active_user)
	permissions = get_permissions(active_user)
	users = get_users(permissions)
	
	return render_template(
		'index.html', 
		user = active_user,
		active_session = active_session,
		sessions = groups, 
		unrated = unrated_ideas,
		rated = rated_ideas,
		permissions = permissions,
		users = users
	)

@app.route('/users')
def update_users():
	permissions = get_permissions()
	users = get_users(permissions)
	return jsonify(users)

@app.route('/sessions', methods=['POST'])
def create_session():
	if request.method == 'POST':
		group = request.get_json()
		new_group = Sessions(title=group['title'], creator=g.user.id)
		db.session.add(new_group)
		db.session.commit()
		group["id"] = new_group.id
		group["lastModified"] = new_group.lastModified
		return _todo_response(group)

@app.route('/ideas')
def get_idea_score():    
	active_session, group_ids, groups = get_sessions()
	unrated_ideas, rated_ideas = get_ideas(group_ids)
	return jsonify(rated_ideas)

@app.route('/ideas', methods=['POST'])
def create_idea():
	idea = request.get_json()
	new_idea = Unranked(
		session = idea['session'],
		name = idea['name']
	)
	db.session.add(new_idea)
	db.session.commit()	
	idea['id'] = new_idea.id
	return _todo_response(idea)

def update_average(idea_id):
	idea = Unranked.query.filter_by(id=idea_id).first()
	scores_q = idea.scores.all()
	scores = [score.score for score in scores_q]
	idea.avg_score = sum(scores)/float(len(scores))
	db.session.commit()

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
	update_average(score["unranked_id"])
	return _todo_response(score)	

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
    me = facebook.get('/me/?fields=email,name,id,picture.height(200).width(200)')
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

@app.route('/permissions', methods=['POST'])
def create_permissions():
	permission = request.get_json()
	permission_q = Permission.query.filter(
		Permission.granter_id == g.user.id
	).filter(
		Permission.granted_id == permission['granted_id']
	).filter(
		Permission.session == permission['session']
	).first()

	if permission_q:
		permission['id'] = permission_q.id
		return _todo_response(permission)
	else:
		new_permission = Permission(
			granter_id = g.user.id,
			granted_id = permission['granted_id'],
			session = permission['session']
		)
		db.session.add(new_permission)
		db.session.commit()
		permission['id'] = new_permission.id
	return _todo_response(permission)

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
        auth_server_id=8,
        name='user8',
        email='email8',
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


@app.route('/query3')
def query_test3():    
    idea = Unranked.query.with_entities(Unranked.id).all()
    return jsonify(idea)
    
    