$(document).ready(function(){
    
    $('#consoleLog').append(localStorage.getItem('consoleLog'));

    $('#completePostInstallationTasks').on('click', function(event) {
        
        $("#completePostInstallationTasks").prop("disabled", true);

        event.preventDefault();
        
        $.ajax({
            url: "/stage5",
            type : "POST",
            contentType: 'application/json',
    
            success: function(response) {
                
                consoleLog = localStorage.getItem('consoleLog');
                consoleLog += $('#consoleLog').val()
                localStorage.setItem('consoleLog', consoleLog);

                $("#completePostInstallationTasks").prop("disabled", false);

            },
            error: function(error) {
                $("#completePostInstallationTasks").prop("disabled", false);
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
