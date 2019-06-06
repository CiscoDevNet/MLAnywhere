$(document).ready(function(){

   
    
    $('#deployKubeflow').on('click', function(event) {
        
        event.preventDefault();
        
        $.ajax({
            url: "/stage4",
            type : "GET",
            contentType: 'application/json',
    
            success: function(response) {
                
                response = JSON.parse(response)

                if (response["redirectURL"] !== undefined) {
                    window.location.replace(response.redirectURL);
                } else {
                    window.location.reload(true);
                }
            },
            error: function(error) {
                $("#alertBox").html(
                    `
                    <div class="alert alert--danger alert-dismissible fade in ">
                        <div class="alert__icon icon-error-outline"></div>
                        <strong>Kubeflow deployment failed</strong>
                        <a href="#" class="close" data-dismiss="alert" aria-label="close">x</a>
                    </div>
                    `
                );
        }
        });
         
    });
     

     

        
         


})
