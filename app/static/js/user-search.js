var app = app || {};

(function(){

  var viewUnratedIdeas = document.getElementById(
    'view-unrated-ideas'
  ).addEventListener(
    'click', app.unratedIdeaListView.showUnratedIdeas
  );

  var viewRatedIdeas = document.getElementById(
    'view-rated-ideas'
  ).addEventListener(
    'click', app.unratedIdeaListView.showRatedIdeas
  );

  var viewPermissions = document.getElementById(
    'view-permissions'
  ).addEventListener(
    'click', app.unratedIdeaListView.showPermissions
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

