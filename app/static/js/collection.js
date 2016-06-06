
var app = app || {};

(function () {

	var SessionList = Backbone.Collection.extend({
	  model: app.Session,
	  url: '/sessions'
	});

	var ideaList = Backbone.Collection.extend({
		model: app.Idea,
		url: '/ideas'
	});

	app.sessionList = new SessionList();
	app.unratedIdeaList = new ideaList();
	app.ratedIdeaList = new ideaList();

})();
