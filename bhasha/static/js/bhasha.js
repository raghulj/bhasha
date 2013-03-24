function getCookie(name)
{
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
 
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
 
$.ajaxSetup({ 
     beforeSend: function(xhr, settings) {
         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
             // Only send the token to relative URLs i.e. locally.
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
         }
     } 
});


function create_event() {
    var title = $("#inputMsgTitle").val();
    var description = $("#inputMsgDescription").val();
    $.ajax({
        type: "POST",
        url:'/projects/create/',
        data:{ "title": title, "description": description},
        datatype: "json",
        success: function(data){
            if (data.status == "success") { // script returned error
                alert(data.message);
                location.reload();
            } 
            else {    
                alert(data.message);
            }
        },
        error: function(XMLHttpRequest, textStatus, errorThrown){
        // alert(errorThrown);
        }
    });
}
