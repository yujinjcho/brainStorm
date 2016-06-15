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

	app.UserView = Backbone.View.extend({
		template: _.template($('#user-template').html()),
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
	    var newModel = app.sessionList.create(this.newSession(), {wait:true, success: function(model){
	    	document.getElementById('new-idea').setAttribute('name', model.get('id'));
	    	app.unratedIdeaListView.addSome();
	    	app.ratedIdeaListView.addSome();
	    	app.userListView.addSome();
	    	app.sessionListView.sessionHighlight();
	  	}});
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
	    //this.manageSessions();
	  },
	  events: {
	    'keypress input#new-idea' : 'add_Idea',
	    'click form.sessions' : 'change_Session',
	    'click form.sessions i' : 'stopProp',
    	'click a#manage-sessions' : 'manageSessions',
    	'click a#show-sessions' : 'showSessions'
	  },
	  add_Idea: function(e){
	    if (e.which !== 13 || !this.input.val().trim()){
	    	return;
	    };

	    if (app.active_session.name == "None"){
	    	alert('Please create a session first')
				this.input.val('');
	    	return;
	    };

	    app.unratedIdeaList.create(this.newIdea(), {wait:true});
	    this.input.val('');
	  },
	  stopProp: function(e) {
	  	e.stopPropagation();
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
	  },
    manageSessions: function(){
      var viewElems = ['unrated-container', 'rated-container'];
      var viewLength = viewElems.length;
      
      var toggleElems = ['group-container'];
      var toggleLength = toggleElems.length;

      for (var i = 0; i < viewLength; i++) {
				document.getElementById(viewElems[i]).classList.add('no-show');      	
      };

      for (var i = 0; i < toggleLength; i++) {
				document.getElementById(toggleElems[i]).classList.remove('no-show');      	
      };
    },
    showSessions: function(){
      var viewElems = ['unrated-container', 'rated-container'];
      var viewLength = viewElems.length;
      
      var toggleElems = ['group-container'];
      var toggleLength = toggleElems.length;

      for (var i = 0; i < viewLength; i++) {
				document.getElementById(viewElems[i]).classList.remove('no-show');      	
      };

      for (var i = 0; i < toggleLength; i++) {
				document.getElementById(toggleElems[i]).classList.add('no-show');      	
      };

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
	  	
  	  app.scoreList.create(this.ratedIdea(idea, score), {success: function(){
  	  	app.ratedIdeaList.fetch({wait:true, reset:true, success:function(){
  	  		app.unratedIdeaList.remove(app.unratedIdeaList.get(parseInt(idea)));
  	  	}});
  	  }})
	  	
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

	app.UserListView = Backbone.View.extend({
	  el: '#container',
	  initialize: function(){
	    app.userList.on('reset', this.addSome, this);
	    this.addSome();
	  },
	  events : {
	  	'click form.sessions' : 'addSome'
	  },
    addOneIf: function(permission){
      if (app.active_session.name == permission.get('session')){
	    	var user = app.userList.get(permission.get('granted_id'))	
	    	var view = new app.UserView({model: user});
	    	$('#user-container').append(view.render().el);	
		    	
	    };
	  },
	  defaultMsg: function(){
	  	if (document.getElementById("user-container").innerHTML == "") {
	  		document.getElementById("user-container").innerHTML = "This is a private session"
	  	};
	  },
	  addSome: function(){ 
      this.$('#user-container').html('');
	    app.permissionList.each(this.addOneIf, this);
	    this.defaultMsg();
	  },
	  update_user: function(){
	  	this.fetch({wait:true, reset: true})
	  }
	});	


})();