$(document).ready(function(){
    
    $('#consoleLog').append(localStorage.getItem('consoleLog'));


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
        createNotebookServer();
    });

    $('#uploadFile').on('click', function() {
        $('#file-input').trigger('click');
    });

    $("#file-input").change(function(){
        uploadFiletoJupyter()
      });

    verifyK8sServices();
    checkIngress();
    checkKubeflowDashboardReachability();



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
            }
            else
            {
                alertClass = "alert alert--danger"
                statusMsg = "Kubernetes pods not running"

            }


            $("#kubernetesPodAlert").empty().html(
                `
                <div class="` + alertClass +`">
                    <div class="alert__icon icon-check-outline"></div>
                    <div class="alert__message">` + statusMsg +`</div>
                </div>
                ` 
            )
           
        },
        error: function(error) {

            $("#viewPods").prop("disabled", true);

            $("#postInstallChecklist").empty().append(
                `
                <div class="alert alert--danger">
                    <div class="alert__icon icon-check-outline"></div>
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
            <div class="alert__message">Creating notebook</div>
        </div>
        ` 
    )  

    $.ajax({
        url: "/createNotebookServer",
        type : "POST",
        contentType: 'application/json',

        success: function(response) {
            
            $("#createNotebook").prop("disabled", false);

            $("#notebookAlert").empty().html(
                `
                <div class="alert alert--success">
                    <div class="alert__icon icon-check-outline"></div>
                    <div class="alert__message">Notebook created</div>
                </div>
                ` 
            )  

        },
        error: function(error) {

            $("#createNotebook").prop("disabled", false);

            $("#notebookAlert").empty().html(
                `
                <div class="alert alert--danger">
                    <div class="alert__icon icon-error-outline"></div>
                    <div class="alert__message">Issue creating notebook</div>
                </div>
                `
            );
        }
    })
}




function uploadFiletoJupyter() {

    var fd = new FormData();

    file = $("#file-input")[0].files[0].name

    lastDot = file.lastIndexOf('.');

    filename = file.substring(0, lastDot);

    fd.append(filename, ($("#file-input"))[0].files[0]);

    $.ajax({
        url: "/uploadFiletoJupyter",
        type : "POST",
        processData: false,
        contentType: false, 
        data:fd,
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
                console.log(IDBIndex)
                console.log(value)
                event_data += '<tr>';
                event_data += '<td align="left">'+value.NAMESPACE+'</td>';
                event_data += '<td align="left">'+value.NAME+'</td>';
                event_data += '<td align="left">'+value.STATUS+'</td>';
                event_data += '</tr>';
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



