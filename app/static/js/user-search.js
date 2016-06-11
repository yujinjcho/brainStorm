$('#autocomplete').autocomplete({
    serviceUrl: '/autocomplete/countries',
    onSelect: function (suggestion) {
        //alert('You selected: ' + suggestion.value + ' ' + suggestion.id.toString();)
        var active_session = document.getElementById('new-idea').name;
        app.permissionList.create({"granted_id":suggestion.id, 'session':active_session});
    }
});	

