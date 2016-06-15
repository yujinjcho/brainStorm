var app = app || {};

(function(){

  var manageSessions = document.getElementById(
    'manage-sessions'
  ).addEventListener(
    'click', app.unratedIdeaListView.manageSessions
  );
  
  var showSessions = document.getElementById(
    'show-sessions'
  ).addEventListener(
    'click', app.unratedIdeaListView.showSessions
  );

  $('#autocomplete').autocomplete({
      serviceUrl: '/autocomplete/countries',
      onSelect: function (suggestion) {
          var active_session = document.getElementById('new-idea').name;
          
          if (app.active_user != suggestion.id) {
        	    app.permissionList.create({"granted_id":suggestion.id, 'session':active_session},{wait:true, success: function(){
                  app.permissionList.fetch({wait:true, reset: true, success: function(){
                      app.userList.fetch({wait:true, reset: true})
                  }})
              }})
          }

          document.getElementById('autocomplete').value='';
      }
  });	

})();

