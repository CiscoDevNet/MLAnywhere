$(document).ready(function(){

    $('#consoleLog').append(localStorage.getItem('consoleLog'));
    
    $('#uploadCluster').on('click', function(event) { 

        event.preventDefault();
        
        var formData = new FormData();
        formData.append('file', $('#file')[0].files[0]);
        //formData.append('clusterName', $('#clusterName').val());
        
        //Check cluster name does not already exist - on success deploy the cluster
        $.ajax({
            type: "POST",
            url:"/existingClusterUpload",
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                if (response.redirectURL) {
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
                        <strong>Cluster upload failed!</strong>
                        <a href="#" class="close" data-dismiss="alert" aria-label="close">x</a>
                    </div>
                    `
                );

                return 
            }
        });  
    });
})