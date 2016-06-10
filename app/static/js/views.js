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
	    app.active_session = document.getElementById('new-idea');
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
	    app.sessionList.create(this.newSession(), {wait:true});
	    this.input.val('');
	  },
	  addSessionCallback: function() {
	  	this.addAll;
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
	    this.sessionHighlight()
	  },
	  sessionHighlight: function() {
	  	app.sessionList.each(this.activeSession, this);
	  },
	  activeSession: function(session){
	  	if (app.active_session.name == session.get('id')){
	  		document.getElementById(app.active_session.name).setAttribute('style', 'background-color: rgba(220, 220, 220, 1)');
	  	} else {
	  		document.getElementById(session.get('id')).setAttribute('style', 'None');
	  	};
	  },
	});

	app.UnratedIdeaListView = Backbone.View.extend({
	  el: '#container',
	  initialize: function(){
	    this.input = this.$('#new-idea');
	    app.active_session = document.getElementById('new-idea');
	    app.unratedIdeaList.on('add', this.addSome, this);
      app.unratedIdeaList.on('remove', this.addSome, this);
	    app.unratedIdeaList.on('reset', this.addSome, this);
	    this.addSome();
	  },
	  events: {
	    'keypress input#new-idea' : 'add_Idea',
	    'click form.sessions' : 'change_Session'
	  },
	  add_Idea: function(e){
	    if (e.which !== 13 || !this.input.val().trim()){
	    	return;
	    };
	    app.unratedIdeaList.create(this.newIdea(), {wait:true});
	    this.input.val('');
	  },
	  add_ideaCallback: function() {
	  	this.addSome;
	  },
	  newIdea: function() {
	  	return {
	  		name: this.input.val().trim(),
	  		session: document.getElementById('new-idea').getAttribute('name')
	  	};
	  },
	  addOneIf: function(idea){
	    if (app.active_session.name == idea.get('session')){
	    	var view = new app.IdeaView({model: idea});
	    	$('#unrated-list').append(view.render().el);	
	    };
	  },
	  addSome: function(){ 
	    this.$('#unrated-list').html('');
	    app.unratedIdeaList.each(this.addOneIf, this);
	    app.sessionListView.sessionHighlight();
	  },
	  change_Session: function(e){	  	
	  	app.active_session.setAttribute('name', e.target.id);
	  	this.addSome();
	  	app.ratedIdeaListView.addSome();
	  }
	});

	app.RatedIdeaListView = Backbone.View.extend({
	  el: '#container',
	  initialize: function(){
	    app.ratedIdeaList.on('reset', this.addSome, this);
	    this.addSome();
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
	  ratedIdea: function(unranked_id, score) {
	  	return {
	  		"unranked_id": unranked_id,
	  		"score": score
	  	};
	  },
	  update_Score: function(e){
		if (e.which !== 13 || 
				e.target.value.trim() == "" || 
				e.target.value > 10 ||
				e.target.value < 0){
	    	return;
	    };
		var idea = e.target.id.slice(1);
	  	var score = e.target.value;
	  	$.when(
	  	  app.scoreList.create(this.ratedIdea(idea, score))
	  	).then(function(){
        app.ratedIdeaList.fetch({wait:true, reset:true});
	  	}).then(function(){
        app.unratedIdeaList.remove(app.unratedIdeaList.get(parseInt(idea)));
      })
	  },
	  addOneIf: function(idea){
      if (app.active_session.name == idea.get('session')){
	    	var view = new app.RatedIdeaView({model: idea});
	    	$('#rated-list').append(view.render().el);	
	    };
	  },
	  addSome: function(){ 
      this.$('#rated-list').html('');
	    app.ratedIdeaList.each(this.addOneIf, this);
	  },
	});


})();