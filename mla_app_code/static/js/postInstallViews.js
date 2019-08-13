$(document).ready(function(){

    $('#consoleLog').append(localStorage.getItem('consoleLog'));

    $('#viewPods').on('click', function(event) {
        
        event.preventDefault();      


        $.ajax({
            type: "GET",
            url:"/viewPods",
            dataType: "json",
            success: function (jsonToDisplay) {

                $("#jsonModal").modal('show');
                
                //$('#jsonModal').find('.modal-body').append('<code><pre style="text-align:justify;">'+JSON.stringify(jsonToDisplay, undefined, 2)+'</pre></code>');
            
                var event_data = '';

                $.each(jsonToDisplay, function(index, value){
                    console.log(IDBIndex)
                    console.log(value)
                    event_data += '<tr>';
                    event_data += '<td align="left">'+value.NAMESPACE+'</td>';
                    event_data += '<td align="left">'+value.NAME+'</td>';
                    event_data += '<td align="left">'+value.STATUS+'</td>';
                    event_data += '</tr>';
                });
                $("#viewModal").append(event_data);
            }
        });
        
     
     });


     

        
         


})
