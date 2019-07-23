post_install_stage = 1

$(document).ready(function(){
    
    $('#consoleLog').append(localStorage.getItem('consoleLog'));

    $("#toggleIngress").prop("disabled", true);
    $("#kubeflowDashboard").prop("disabled", true);
    $("#createNotebook").prop("disabled", true);
    $("#uploadFile").prop("disabled", true);

    $('#viewPods').on('click', function(event) {
        event.preventDefault();      
        viewPods();
    });

    $('#toggleIngress').on('click', function(event) {
        event.preventDefault();      
        toggleIngress();
    });

    $('#kubeflowDashboard').on('click', function(event) {
        event.preventDefault();      
        kubeflowDashboard();
    });

    $('#createNotebook').on('click', function(event) {
        event.preventDefault();      
        openNotebookServer();
    });

    $('#uploadFile').on('click', function() {
        uploadFiletoJupyter()
    });

    verifyPostInstall()
    setInterval(verifyPostInstall,5000);
});

function verifyK8sServices() {

    $.ajax({
        type: "GET",
        url:"/viewPods",
        dataType: "json",
        success: function (jsonToDisplay) {
            
            success = true;
            
            $.each(jsonToDisplay, function(index, value){
               
                if (!(value.STATUS == "Running" || value.STATUS == "Succeeded"))
                {
                    success = false
                }

            });

            alertClass = "alert alert--danger"

            if (success)
            {
                alertClass = "alert alert--success"
                statusMsg = "Kubernetes pods running"
                $("#kubernetesPodAlert").empty().html(
                    `
                    <div class="` + alertClass +`">
                        <div class="alert__icon icon-check-outline"></div>
                        <div class="alert__message">` + statusMsg +`</div>
                    </div>
                    ` 
                )
                post_install_stage = 2
            }
            else
            {
                alertClass = "alert alert--warning"
                statusMsg = "Waiting for Kubernetes pods to start"
                $("#kubernetesPodAlert").empty().html(
                    `
                    <div class="` + alertClass +`">
                        <div class="alert__icon icon-error-outline"></div>
                        <div class="alert__message">` + statusMsg +`</div>
                    </div>
                    ` 
                )
            }
        },
        error: function(error) {

            $("#viewPods").prop("disabled", true);

            $("#postInstallChecklist").empty().append(
                `
                <div class="alert alert--danger">
                    <div class="alert__icon icon-error-outline"></div>
                    <div class="alert__message">Error running post install check</div>
                </div>
                ` 
            )
        }
    });
}

function toggleIngress() {

    $("#toggleIngress").prop("disabled", true);

    $.ajax({
        url: "/toggleIngress",
        type : "POST",
        contentType: 'application/json',

        success: function(jsonToDisplay) {
            
            $("#toggleIngress").prop("disabled", false);

            $("#ingressAlert").empty().html(
                `
                <div class="alert alert--success">
                    <div class="alert__icon icon-check-outline"></div>
                    <div class="alert__message">Cluster access configured as ` + jsonToDisplay.ACCESSTYPE +` on address ` + jsonToDisplay.IP +`</div>
                </div>
                ` 
            )  

        },
        error: function(error) {

            $("#toggleIngress").prop("disabled", false);

            $("#ingressAlert").empty().html(
                `
                <div class="alert alert--danger">
                    <div class="alert__icon icon-error-outline"></div>
                    <div class="alert__message">Issue retrieving ingress details</div>
                </div>
                `
            );
        }
    })
}

function createNotebookServer() {

    $("#createNotebook").prop("disabled", true);

    $("#notebookAlert").empty().html(
        `
        <div class="alert alert--warning">
            <div class="alert__icon icon-check-outline"></div>
            <div class="alert__message">Creating Notebook Server</div>
        </div>
        ` 
    )  

    $.ajax({
        url: "/createNotebookServer",
        type : "POST",
        contentType: 'application/json',

        success: function(response) {
            
            $("#createNotebook").prop("disabled", true);
            $("#uploadFile").prop("disabled", false);

            $("#notebookAlert").empty().html(
                `
                <div class="alert alert--warning">
                    <div class="alert__icon icon-check-outline"></div>
                    <div class="alert__message">Creating Notebook Server</div>
                </div>
                ` 
            )  

        },
        error: function(error) {

            $("#createNotebook").prop("disabled", true);

            $("#notebookAlert").empty().html(
                `
                <div class="alert alert--danger">
                    <div class="alert__icon icon-error-outline"></div>
                    <div class="alert__message">Issue creating Notebook Server</div>
                </div>
                `
            );
        }
    })
}

function verifyNotebooks() {

    $("#uploadFile").prop("disabled", true);

    $.ajax({
        url: "/verifyNotebooks",
        type : "GET",
        contentType: 'application/json',

        success: function(response) {

            if (typeof Object.keys(response) !== 'undefined' && Object.keys(response).length > 0) {
                console.log(response)
                
                //REAL SUCCESS
                $("#createNotebook").prop("disabled", false);
                $("#notebookAlert").empty().html(
                    `
                    <div class="alert alert--success">
                        <div class="alert__icon icon-check-outline"></div>
                        <div class="alert__message">Notebook created</div>
                    </div>
                    ` 
                )
                uploadFiletoJupyter()
                
                //TODO: not ready yet response (being created)
            }
            else {
                $("#uploadFile").prop("disabled", true);
                $("#notebookAlert").empty().html(
                    `
                    <div class="alert alert--info">
                        <div class="alert__icon icon-check-outline"></div>
                        <div class="alert__message">Error during Notebook Server creation</div>
                    </div>
                    ` 
                )  
            }
            
            

        },
        error: function(error) {

            $("#uploadFile").prop("disabled", false);

            $("#notebookAlert").empty().html(
                `
                <div class="alert alert--danger">
                    <div class="alert__icon icon-error-outline"></div>
                    <div class="alert__message">There was a problem verifying the notebooks</div>
                </div>
                `
            );
        }
    })
}



function uploadFiletoJupyter() {

    var fd = new FormData();

    $.ajax({
        url: "/uploadFiletoJupyter",
        type : "POST",
        processData: false,
        contentType: false, 
        data:{},
        success: function(response) {

            $("#notebookFileAlert").empty().html(
                `
                <div class="alert alert--success">
                    <div class="alert__icon icon-check-outline"></div>
                    <div class="alert__message">File uploaded to Jupyter notebook</div>
                </div>
                ` 
            )  

        },
        error: function(error) {

            $("#notebookFileAlert").empty().html(
                `
                <div class="alert alert--danger">
                    <div class="alert__icon icon-error-outline"></div>
                    <div class="alert__message">Issue uploading file to Jupyter notebook</div>
                </div>
                `
            );
        }
    })
}

function checkIngress() {

    $.ajax({
        url: "/checkIngress",
        type : "GET",
        contentType: 'application/json',

        success: function(jsonToDisplay) {

            $("#ingressAlert").empty().html(
                `
                <div class="alert alert--success">
                    <div class="alert__icon icon-check-outline"></div>
                    <div class="alert__message">Cluster access configured as ` + jsonToDisplay.ACCESSTYPE +` on address ` + jsonToDisplay.IP +`</div>
                </div>
                ` 
            )
            post_install_stage = 3
        },
        error: function(error) {

            $("#toggleIngress").prop("disabled", true);

            $("#ingressAlert").empty().html(
                `
                <div class="alert alert--danger">
                <div class="alert__icon icon-error-outline"></div>
                <div class="alert__message">Issue retrieving ingress details</div>
            </div>
                `
            );
        }
    })
}

function checkKubeflowDashboardReachability() {

    $.ajax({
        url: "/checkKubeflowDashboardReachability",
        type : "GET",
        contentType: 'application/json',

        success: function(jsonToDisplay) {
            $("#kubeflowDashboardAlert").empty().html(
                `
                <div class="alert alert--success">
                    <div class="alert__icon icon-check-outline"></div>
                    <div class="alert__message">Kubeflow dashboard is available</div>
                </div>
                ` 
            )
            createNotebookServer()
            post_install_stage = 4
        },
        error: function(error) {

            $("#kubeflowDashboard").prop("disabled", true);

            $("#kubeflowDashboardAlert").empty().html(
                `
                <div class="alert alert--danger">
                    <div class="alert__icon icon-error-outline"></div>
                    <div class="alert__message">Kubeflow dashboard is not available</div>
                </div>
                `
            );
        }
    })
}

function kubeflowDashboard() {

    $.ajax({
        url: "/checkIngress",
        type : "GET",
        contentType: 'application/json',

        success: function(jsonToDisplay) {
            
            url = "http://" + jsonToDisplay.IP
            window.open(url)

        },
        error: function(error) {

            $("#ingressAlert").empty().html(
                `
                <div class="alert alert--danger">
                <div class="alert__icon icon-error-outline"></div>
                <div class="alert__message">Issue retrieving Kubeflow Dashboard details</div>
            </div>
                `
            );
        }
    })
}

function viewPods() {

    $.ajax({
        type: "GET",
        url:"/viewPods",
        dataType: "json",
        success: function (jsonToDisplay) {
    
            $("#jsonModal").modal('show');
            
            var event_data = '';
    
            $.each(jsonToDisplay, function(index, value){

                if (!((value.STATUS == "Running" ) || (value.STATUS == "Succeeded")))
                {
                    event_data += '<tr style="color:red">';
                    event_data += '<td align="left" >'+value.NAMESPACE+'</td>';
                    event_data += '<td align="left">'+value.NAME+'</td>';
                    event_data += '<td align="left">'+value.STATUS+'</td>';
                    event_data += '</tr>';
                }
                else 
                {
                    event_data += '<tr>';
                    event_data += '<td align="left">'+value.NAMESPACE+'</td>';
                    event_data += '<td align="left">'+value.NAME+'</td>';
                    event_data += '<td align="left">'+value.STATUS+'</td>';
                    event_data += '</tr>';
                }
                
            });
            $("#viewModal").empty().append(event_data);
        },
        error: function(error) {

            $("#alertBox").html(
                `
                <div class="alert alert--danger alert-dismissible fade in ">
                    <div class="alert__icon icon-error-outline"></div>
                    <strong>Issue retrieving pod details</strong>
                    <a href="#" class="close" data-dismiss="alert" aria-label="close">x</a>
                </div>
                `
            );
        }
    });
}

function openNotebookServer() {
    $.ajax({
        url: "/checkIngress",
        type : "GET",
        contentType: 'application/json',

        success: function(jsonToDisplay) {
            
            url = "http://" + jsonToDisplay.IP + '/notebook/kubeflow/mla-notebook'
            window.open(url)

        },
        error: function(error) {

            $("#ingressAlert").empty().html(
                `
                <div class="alert alert--danger">
                <div class="alert__icon icon-error-outline"></div>
                <div class="alert__message">Issue retrieving Notebook Server Dashboard details</div>
            </div>
                `
            );
        }
    }) 
}

function verifyPostInstall() {
    if(post_install_stage == 1) {
        verifyK8sServices();
    } else if(post_install_stage == 2) {
        checkIngress();
    } else if(post_install_stage == 3) {
        checkKubeflowDashboardReachability();
    } else if(post_install_stage == 4) {
        verifyNotebooks();
    }
}
