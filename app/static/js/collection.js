
var app = app || {};

(function () {

	var SessionList = Backbone.Collection.extend({
	  model: app.Session,
	  url: '/sessions',
	  parse: function(response){
	  	return response.collection;
	  }
	});

	var IdeaList = Backbone.Collection.extend({
		model: app.Idea,
		url: '/ideas'
	});

	var ScoreList = Backbone.Collection.extend({
		model: app.Score,
		url: '/scores'
	});

	var PermissionList = Backbone.Collection.extend({
		model: app.Permission,
		url: '/permissions'
	});

	var UserList = Backbone.Collection.extend({
		model: app.User,
		url: '/users'
	})

	app.sessionList = new SessionList();
	app.sessionList.comparator = function(att){
		return -Date.parse(att.get('lastModified'));
	};

	app.unratedIdeaList = new IdeaList();
	app.ratedIdeaList = new IdeaList();
	app.ratedIdeaList.comparator = function(att){
		return -parseInt(att.get('score'));
	};
	app.scoreList = new ScoreList();
	app.permissionList = new PermissionList();
	app.userList = new UserList();

})();
