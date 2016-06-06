from app import app
from flask import render_template, request, jsonify, url_for

groups = [{"title": "session"}]
unrated_ideas = []
rated_ideas = [{"session":"session 1","name":"yooo","score":8}]
active_session = "session1"


@app.route('/')
def index():
	return render_template(
		'index.html', 
		sessions = groups, 
		unrated = unrated_ideas,
		rated = rated_ideas,
		active_session = active_session
	)

@app.route('/sessions', methods=['POST'])
def group_create():
	if request.method == 'POST':
		group = request.get_json()
		groups.append({"title": group['title']})
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
			unrated_ideas.append({"session": idea['session'], "name": idea['name']})
		return _todo_response(idea)

def _todo_response(data):
    return jsonify(**data)