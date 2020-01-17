post_install_stage = 1

$(document).ready(function(){
    
    $('#consoleLog').append(localStorage.getItem('consoleLog'));
    
    $("#gotokf").prop("disabled", true);
    
    $('#viewpods').on('click', function(event) {
        event.preventDefault();      
        viewPods();
    })
                      
    $('#gotokf').on('click', function(event) {
        event.preventDefault();      
        viewPods();
    })
    
    setUpPage()

    verifyPostInstall()
    setInterval(verifyPostInstall,5000);
});


row_template = 
    `
    <div class="row resultrow">
        <div class="col-md-7" style="margin: 0 auto;">
            <div>
                <div class="alert alert--info">
                    <div class="alert__icon"></div>
                    <div class="alert__message">{replace-text}</div>
                </div>
            </div>
        </div>
    </div>
    `

button_template =
    `
    <input type="submit" class="btn btn--primary stage4btn1" value="Go to KubeFlow" onclick="window.open('http://{replace-ip}')">
    `

function setUpPage() {
    stages = [
        "Waiting for MLA pod to be deployed",
        "Upgrading Helm",
        "Setting up NFS server",
        "Setting up Kubeflow",
        "Waiting for all Pods to be ready",
        "Changing the default Storage Class",
        "Creating PVC",
        "Getting IP and port for Kubeflow dashboard",
        "Creating the demo namespace",
        "Creating notebook server",
        "Waiting for notebook server to be ready",
        "Uploading demos to notebook server",
        "Installing additional modules for notebook server",
        "Giving full permissions to namespace"
    ]
    
    for(var i=0;i<stages.length;i++) {
        row = row_template.replace(
            /{replace-text}/g,
            stages[i]
        )
        
        $('#installprogress').append(row)
    }
}

function verifyPostInstall() {
    let searchParams = new URLSearchParams(window.location.search)
//    if(searchParams.has('cluster')) {
//        cluster = searchParams.get('cluster')
//    } else {
//        cluster == ''
//    }
    
    
    $.ajax({
        type: "GET",
        url:"/mladeploymentstatus",
        //data: {cluster : cluster},
        success: function (response) {
            steps = [{'name': "Waiting for MLA pod to be deployed", 'entries': []}]
            if(response != 'Pod not reachable yet') {
                var logs = JSON.parse(response)

                steps = []
                for(var i=0;i<logs.length;i++) {
                    if(/-------------- [A-Z a-z ]* --------------/.test(logs[i])) {
                        steps.push({
                            'name': logs[i].replace('-------------- ', '').replace(' --------------', ''),
                            'entries': []
                        })
                    } else {
                        steps[steps.length-1]['entries'].push(logs[i])
                    }
                }
            }
            for(var i=0;i<steps.length;i++){
                if(i == steps.length-1) {
                    console.log('LAST ELEMENT!')
                } else {
                    console.log('FINISHED ELEMENT!')
                }
                console.log($('#installprogress').children()[i].children[0].children[0].children[0])
            } 
            
            console.log(steps[steps.length-1])
        },
        error: function(error) {
            $("#alertBox").html(
                `
                <div class="alert alert--danger alert-dismissible fade in ">
                    <div class="alert__icon icon-error-outline"></div>
                    <strong>Issue retrieving MLA setup details</strong>
                    <a href="#" class="close" data-dismiss="alert" aria-label="close">x</a>
                </div>
                `
            );
        }
    });
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

