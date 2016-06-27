
var app = app || {};

(function () {

	app.Session = Backbone.Model.extend({
		defaults:{name:''},
		getTitle:function(){
		  return this.name;
	  }
	});

	app.Idea = Backbone.Model.extend({
		defaults : {
			session : '', 
			name : ''
		}
	});

	app.Score = Backbone.Model.extend({
		defaults : {
			unranked_id: '',
			user_id: '',
			score: '',
		}
	});

	app.Permission = Backbone.Model.extend({
		defaults : {
			session: '',
			granted_id: ''
		}
	});

	app.User = Backbone.Model.extend({
		defaults : {
			profile_pic: "",
			name: ""
		}
	});
})();
