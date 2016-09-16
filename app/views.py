"""Idea Storm is a web application that allows a user to create ideas,
add other users to a session, and collaboratively rank ideas.

"""

from operator import itemgetter
import json
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
    IdeaSession,
    Idea, 
    User, 
    Score, 
    Permission
)

@app.route('/logout')
def logout():
    """Logout current user"""
    logout_user()
    return redirect(url_for('index'))

@app.before_request
def get_current_user():
    """Assign current user to g object"""
    ########################################
    #FOR TESTING PURPOSES
    #user = User.query.filter(User.name == 'user25').first()
    #user = User.query.filter(User.name == 'Yujin Cho').first()
    
    #login_user(user, remember=True)
    ########################################
    
    g.user = current_user

def get_sessions():
    """Get sessions for current user based on permissions"""
    permissions = Permission.query.filter(Permission.granted_id == g.user.id).all() 
    permission_set = set([p.idea_session_id for p in permissions])
    if not permissions:
        permitted_sessions = []
    else:
        permitted_sessions = IdeaSession.query.filter(IdeaSession.id.in_(permission_set)).all()

    groups = sorted([s.json_view() for s in permitted_sessions], key=itemgetter('created'))
    group_ids = [int(s.id) for s in permitted_sessions]

    if not group_ids:
        active_session = None
    else:
        active_session = groups[-1]['id']

    return active_session, group_ids, groups

def get_ideas(group_ids):
    """Get ideas for current user based on idea session ids and
    separate ideas into ranked and not ranked groups

    :param list group_ids: idea session ids
    """
    scores = Score.query.filter(Score.user_id == g.user.id).all()
    scored_ideas = [score.idea_id for score in scores]
    unrated_q = Idea.query.filter(Idea.idea_session_id.in_(set(group_ids))).all()
    
    unrated_ideas = [
        idea.json_view() for idea in unrated_q 
        if idea.id not in scored_ideas
    ]
    rated_ideas = [
        idea.json_view() for idea in unrated_q 
        if idea.id in scored_ideas
    ]
    return unrated_ideas, rated_ideas

def get_permissions(group_ids):
    """Get permissions associated with various idea sessions

    :param list group_ids: idea session ids
    """
    all_permissions = Permission.query.all()
    
    if not all_permissions:
        permissions_query = []
    else:
        permissions_query = [p for p in all_permissions if p.idea_session_id in group_ids]
    
    permissions_granted = [
        {'granted_id': permission.granted_id, 
         "session": permission.idea_session_id}
        for permission in all_permissions
    ]
    
    combined_permissions = permissions_granted
    permitted_json = [json.dumps(p, sort_keys=True) for p in combined_permissions]
    permitted_set = [json.loads(p) for p in list(set(permitted_json))]
    return permitted_set


def get_users(permissions):
    """Get users associated with given permissions

    :param list permissions: permission ids
    """
    user_creators = User.query.all()
    users = [u.json_view() for u in user_creators]
    return users

def commit_session(name, id):
    """Saves newly created session and permission to db. Returns
    newly created session.

    :param str name: name of idea session
    :param int id: user id of creator
    """
    new_idea_session = IdeaSession(name=name, creator_id=id)
    db.session.add(new_idea_session)
    db.session.commit()

    new_permission = commit_permission(g.user.id, new_idea_session.id)
    db.session.add(new_permission)
    db.session.commit()    

    return new_idea_session

def guest_login():
    """Logs in user as guest user. Create guest account if it 
    doesn't exist.
    """
    user = User.query.filter(User.email == 'guest_account').first()
    if not user:
        user = User(
            auth_server_id='Guest',
            name='Guest',
            email='guest_account',
            profile_pic='Guest'
        )
        db.session.add(user)
    
    login_user(user, remember=True)
    db.session.commit()
    

@app.route('/')
def index():
    """Returns page based on logged in user

    Sets active user. Finds idea sessions for active user.
    Finds ideas associated with sessions based on whether
    user voted on or not. Find permissions for idea sessions.
    Get information for other users based on permissions.
    """
    if not g.user.is_authenticated:
        guest_login()
        return redirect(url_for('index'))
    
    active_user = g.user
    active_session, group_ids, groups = get_sessions()
    unrated_ideas, rated_ideas = get_ideas(group_ids)
    permissions = get_permissions(group_ids)
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
    """Return users associated with session ides in JSON"""
    active_session, group_ids, groups = get_sessions()
    permissions = get_permissions(group_ids)
    users = get_users(permissions)
    return jsonify(users)

@app.route('/sessions', methods=['POST'])
def create_session():
    """Receives JSON from client and creates new idea session"""    
    idea_session = request.get_json()

    new_idea_session = commit_session(name=idea_session['name'], id=g.user.id)

    idea_session["id"] = new_idea_session.id
    idea_session["created"] = new_idea_session.created
    idea_session["creator_id"] = new_idea_session.creator_id

    return _todo_response(idea_session)

@app.route('/ideas')
def get_idea_score():   
    """Returns rated ideas in JSON""" 
    active_session, group_ids, groups = get_sessions()
    unrated_ideas, rated_ideas = get_ideas(group_ids)
    return jsonify(rated_ideas)

@app.route('/ideas', methods=['POST'])
def create_idea():
    """Receives JSON and stores new Idea to db"""

    idea = request.get_json()
    new_idea = Idea(
        idea_session_id = idea['session'],
        name = idea['name'],
        creator_id = g.user.id
    )
    db.session.add(new_idea)
    db.session.commit() 
    idea['id'] = new_idea.id
    idea['description'] = None
    idea['creator_id'] = g.user.id
    return _todo_response(idea)

@app.route('/ideas/<int:idea_id>', methods=['PUT'])
def update_description(idea_id):
    """Receives JSON and updates description for a specified idea"""
    idea = request.get_json()
    update_idea = Idea.query.filter(Idea.id == idea_id).first()
    update_idea.description = idea['description']
    db.session.add(update_idea)
    db.session.commit()
    idea["id"] = update_idea.id
    return _todo_response(idea)

@app.route('/scores', methods=['POST'])
def create_score():
    """Creates a new score for a specified idea"""
    score = request.get_json()
    new_score = Score(
        idea_id = score["idea_id"],
        user_id = g.user.id,
        score = score["score"]
    )
    db.session.add(new_score)
    db.session.commit()
    score['id'] = new_score.id
    score['user_id'] = g.user.id
    return _todo_response(score)

def _todo_response(data):
    """Returns data in JSON format"""
    return jsonify(**data)

@app.route('/login')
def login():
    """Redirects user to FB auth. process if new user or else will
    automaticaly log user in.

    """
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
    """Manages fb response for auth request"""
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
    """Gets OAuth token"""
    return session.get('oauth_token')

def set_user(me):
    """After successful Auth. process, logs in user"""
    user = User.query.filter_by(
        auth_server_id=me.data['id']
    ).first()
    if user is None:
        user = create_user(me)

    login_user(user, remember=True)
    return redirect(url_for('index'))

def create_user(me): 
    """creates new user and stores to db""" 
    new_user = User(
        auth_server_id=me.data['id'],
        name=me.data['name'],
        email=me.data['email'],
        profile_pic=me.data['picture']['data']['url']
    )  

    db.session.add(new_user)
    db.session.commit()
    login_user(new_user, remember=True)
    commit_session('Session 1', new_user.id)
    return new_user

@lm.user_loader
def load_user(id):
    """Queries db and returns user based on id"""
    if id == "None":
        return None
    return User.query.get(int(id))

@app.route('/autocomplete/countries')
def autocomplete_countries():
    """Returns users that fit criteria for autocomplete search"""
    query = request.args.get('query')
    query_term = '%'+'%'.join(query.split('+'))+'%'
    users = User.query.filter(User.name.ilike(query_term)).all()
    users_list = [{"value": user.name, "id":user.id} for user in users if user.auth_server_id != 'Guest']
    response = { "suggestions": users_list}
    return jsonify(response)

@app.route('/permissions', methods=['POST'])
def create_permissions():
    """Creates a permission for a user when granted by another user"""
    permission = request.get_json()

    permission_q = Permission.query.filter(
        Permission.granted_id == permission['granted_id']
    ).filter(
        Permission.idea_session_id == permission['session']
    ).first()

    if permission_q:
        permission['id'] = permission_q.id
        return _todo_response(permission)

    new_permission = commit_permission(permission['granted_id'], permission['session'])
    permission['id'] = new_permission.id
    return _todo_response(permission)

def commit_permission(id, idea_session_id):
    """Save newly created permission to db

    :param int id: id for user who receives permission
    :param int idea_session_id: id for associated session
    """
    new_permission = Permission(
        granted_id = id,
        idea_session_id = idea_session_id
    )
    db.session.add(new_permission)
    db.session.commit()
    return new_permission

@app.route('/permissions')
def update_permissions():
    """Returns most current permissions in JSON format"""
    active_session, group_ids, groups = get_sessions()
    permissions = get_permissions(group_ids)
    return jsonify(permissions)




