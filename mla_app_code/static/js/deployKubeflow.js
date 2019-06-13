$(document).ready(function(){
    
    $('#consoleLog').append(localStorage.getItem('consoleLog'));

    $('#deployKubeflow').on('click', function(event) {
        
        $("#deployKubeflow").prop("disabled", true);

        event.preventDefault();
        
        $.ajax({
            url: "/stage3",
            type : "POST",
            contentType: 'application/json',
    
            success: function(response) {
                
                consoleLog = localStorage.getItem('consoleLog');
                consoleLog += $('#consoleLog').val()
                localStorage.setItem('consoleLog', consoleLog);

                $("#deployKubeflow").prop("disabled", false);
                

                if (response.redirectURL) {
                    window.location.replace(response.redirectURL);
                } else {
                    window.location.reload(true);
                }
            },
            error: function(error) {
                $("#deployKubeflow").prop("disabled", false);
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
     

     

        
         


});
