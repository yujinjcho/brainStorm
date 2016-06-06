var app = app || {};

(function (){
	
	//----------------------
	// Model View
	//----------------------
	app.SessionView = Backbone.View.extend({
	  template: _.template($('#session-template').html()),
	  render: function(){
	    this.$el.html(this.template(this.model.toJSON()));
	    return this;
	  },
	  initialize: function(){
	    this.render();
	  },
	  changeTitle: function(name){
	    this.model.set({title:name});
	    this.render();
	  }
	});

	app.IdeaView = Backbone.View.extend({
	  template: _.template($('#idea-template').html()),
	  render: function(){
	    this.$el.html(this.template(this.model.toJSON()));
	    return this;
	  },
	  initialize: function(){
	    this.render();
	  }
	});

	app.RatedIdeaView = Backbone.View.extend({
	  template: _.template($('#rated-idea-template').html()),
	  render: function(){
	    this.$el.html(this.template(this.model.toJSON()));
	    return this;
	  },
	  initialize: function(){
	    this.render();
	  }
	});	




	//----------------------
	// Collection View
	//----------------------
	app.SessionListView = Backbone.View.extend({
	  el: '#container',
	  initialize: function(){
	    this.input = this.$('#session-name');
	    app.sessionList.on('add', this.addAll, this);
	    this.addAll();
	  },
	  events: {
	    'keypress #session-name' : 'add_Session'
	  },
	  add_Session: function(e){
	    if (e.which !==13 || !this.input.val().trim()){
	    	return;
	    };
	    app.sessionList.create(this.newSession());
	    this.input.val('');
	  },
	  newSession: function() {
	  	return {
	  		title: this.input.val().trim()
	  	};
	  },
	  addOne: function(title){
	    var view = new app.SessionView({model: title});
	    $('#brainstorm-list').append(view.render().el)
	  },
	  addAll: function(){
	    this.$('#brainstorm-list').html('');
	    app.sessionList.each(this.addOne, this);
	  }
	});

	app.UnratedIdeaListView = Backbone.View.extend({
	  el: '#container',
	  initialize: function(){
	    this.input = this.$('#new-idea');
	    app.unratedIdeaList.on('add', this.addAll, this);
	    this.addAll();
	  },
	  events: {
	    'keypress #new-idea' : 'add_Idea'
	  },
	  add_Idea: function(e){
	    if (e.which !== 13 || !this.input.val().trim()){
	    	return;
	    };
	    app.unratedIdeaList.create(this.newIdea());
	    this.input.val('');
	  },
	  newIdea: function() {
	  	return {
	  		name: this.input.val().trim(),
	  		session: document.getElementById('new-idea').getAttribute('name')
	  	};
	  },
	  addOne: function(title){
	    var view = new app.IdeaView({model: title});
	    $('#unrated-list').append(view.render().el)
	  },
	  addAll: function(){
	    this.$('#unrated-list').html('');
	    app.unratedIdeaList.each(this.addOne, this);
	  }
	});

	app.RatedIdeaListView = Backbone.View.extend({
	  el: '#container',
	  initialize: function(){
	    app.ratedIdeaList.on('add', this.addAll, this);
	    this.addAll();
	  },
	  events: {
	    'keypress .score' : 'update_Score'
	  },
	  addOne: function(title){
	    var view = new app.RatedIdeaView({model: title});
	    $('#rated-list').append(view.render().el)
	  },
	  addAll: function(){
	    this.$('#rated-list').html('');
	    app.ratedIdeaList.each(this.addOne, this);
	  },
	  ratedIdea: function(idea, score) {
	  	return {
	  		name: idea,
	  		session: 'session',
	  		score: score
	  	};
	  },
	  update_Score: function(e){
		if (e.which !== 13 || 
				e.target.value.trim() == "" || 
				e.target.value > 10 ||
				e.target.value < 0){
	    	return;
	    };
		idea = e.target.name;
	  	score = e.target.value;
	  	app.ratedIdeaList.create(this.ratedIdea(idea, score));
	  }
	});


})();