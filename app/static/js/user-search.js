var app = app || {};

$('#autocomplete').autocomplete({
    serviceUrl: '/autocomplete/countries',
    onSelect: function (suggestion) {
        //alert('You selected: ' + suggestion.value + ' ' + suggestion.id.toString();)
        var active_session = document.getElementById('new-idea').name;
        $.when(
	  	    app.permissionList.create({"granted_id":suggestion.id, 'session':active_session},{wait:true})
	  	  ).then(function(){
          app.userList.fetch({wait:true, reset: true})
	  	  }).then(function(){
          document.getElementById('autocomplete').value='';
        })

	  	//app.ratedIdeaList.fetch({wait:true, reset:true});

        //app.permissionList.create(
        //	{"granted_id":suggestion.id, 'session':active_session},
        //	{wait:true, success: function(){app.userList.fetch}}
        //);
    }
});	
