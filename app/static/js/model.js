
var app = app || {};

(function () {

	app.Session = Backbone.Model.extend({
		defaults:{title:''},
		getTitle:function(){
		  return this.title;
	  }
	});

	app.Idea = Backbone.Model.extend({
		defaults : {
			session : '', 
			name : ''
		}
	});

})();
