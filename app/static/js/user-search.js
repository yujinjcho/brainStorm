var app = app || {};
var manageSessions = document.getElementById('manage-sessions').addEventListener('click', app.unratedIdeaListView.manageSessions);
var showSessions = document.getElementById('show-sessions').addEventListener('click', app.unratedIdeaListView.showSessions);

$('#autocomplete').autocomplete({
    serviceUrl: '/autocomplete/countries',
    onSelect: function (suggestion) {
        //alert('You selected: ' + suggestion.value + ' ' + suggestion.id.toString();)
        var active_session = document.getElementById('new-idea').name;
        
        if (app.active_user != suggestion.id) {
      	    app.permissionList.create({"granted_id":suggestion.id, 'session':active_session},{wait:true, success: function(){
                app.userList.fetch({wait:true, reset: true})
            }})
        }

        document.getElementById('autocomplete').value='';
	  	//app.ratedIdeaList.fetch({wait:true, reset:true});

        //app.permissionList.create(
        //	{"granted_id":suggestion.id, 'session':active_session},
        //	{wait:true, success: function(){app.userList.fetch}}
        //);
    }
});	



