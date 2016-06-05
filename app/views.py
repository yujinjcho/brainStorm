from app import app
from flask import render_template, request, jsonify, url_for

groups = [{"title": "session1"},{"title": "session2"},{"title": "session4"},{"title": "session5"}]
unrated_ideas = [{"session":"session1", "name":"cool idea 1"},{"session":"session1", "name":"cool idea 2"},{"session":"session1", "name":"cool idea 4"}]
active_session = "session1"


@app.route('/')
def index():
	return render_template(
		'index.html', 
		sessions=groups, 
		unrated=unrated_ideas,
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
		unrated_ideas.append({"session": idea['session'], "name": idea['name']})
		return _todo_response(idea)



def _todo_response(data):
    return jsonify(**data)