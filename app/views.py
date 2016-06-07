from app import app, db
from flask import render_template, request, jsonify, url_for
from models import Sessions, Unranked, Ranked

rated_ideas = [{"session":"session 1","name":"yooo","score":8}]
active_session = "1"

@app.route('/')
def index():
	groups_query = Sessions.query.all()
	groups = [{"id": group.id, "title": group.title} for group in groups_query]

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

@app.route('/sessions')
def get_group():
	groups_query = Sessions.query.all()	
	return jsonify(collection=[json_view(i) for i in groups_query])

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

'''
def _todo_response_list(data_list):
    groups = [{"id": group.id, "title": group.title} for group in data_list]
    return jsonify(collection = groups)
'''