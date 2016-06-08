from app import app, db
from flask import render_template, request, jsonify, url_for
from models import Sessions, Unranked, Ranked
from sqlalchemy import desc

rated_ideas = [{"session":"session 1","name":"yooo","score":8}]


@app.route('/')
def index():
	groups_query = Sessions.query.order_by(desc(Sessions.lastModified)).all()
	groups = [{
		"id": group.id, 
		"title": group.title
	} for group in groups_query]
	active_session = groups_query[0].id

	#unrated_query = Unranked.query.filter_by(session=str(active_session)).all()
	unrated_query = Unranked.query.all()
	unrated_ideas = [
		{"id": unrated.id, "session": unrated.session, "name": unrated.name}
		 for unrated in unrated_query
	]

	return render_template(
		'index.html', 
		sessions = groups, 
		unrated = unrated_ideas,
		rated = rated_ideas,
		active_session = active_session
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
		group = request.get_json()
		new_group = Sessions(title = group['title'])
		db.session.add(new_group)
		db.session.flush()
		group = {"id": new_group.id, "title": new_group.title}
		db.session.commit()
		return _todo_response(group)

@app.route('/ideas')
def get_ideas():    
    unrated_query = Unranked.query.all()
    unrated_ideas = [
        {"id": unrated.id, "session": unrated.session, "name": unrated.name}
         for unrated in unrated_query
    ]
    return jsonify(unrated_ideas)

@app.route('/ideas', methods=['POST'])
def idea_create():
	if request.method == 'POST':
		idea = request.get_json()
		if 'score' in idea:
			rated_ideas.append({
				"session": idea['session'], 
				"name": idea['name'], 
				"score": idea['score']
			})
		else:
			new_idea = Unranked(session = idea['session'], name = idea['name'])
			db.session.add(new_idea)
			db.session.commit()
		return _todo_response(idea)

def _todo_response(data):
    return jsonify(**data)
