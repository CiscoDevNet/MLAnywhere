post_install_stage = 1

$(document).ready(function(){
    
    $('#consoleLog').append(localStorage.getItem('consoleLog'));

    $('#viewPods').on('click', function(event) {
        event.preventDefault();      
        viewPods();
    });

    verifyPostInstall()
    setInterval(verifyPostInstall,5000);
});


row_template = 
    `
    <div class="row resultrow">
        <div class="col-md-7">
            <div>
                <div class="alert alert--{replace-done}">
                    <div class="alert__icon icon-check-outline"></div>
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

function verifyPostInstall() {
    $.ajax({
        type: "GET",
        url:"/mladeploymentstatus",
        success: function (response) {
            if(response == 'Pod not reachable yet') {
                $('#installprogress').html('Waiting for Pods to become ready')
            } else {
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

                $('#installprogress').html('')

                for(var i=0;i<steps.length;i++) {
                    if(i==steps.length-1) {
                        last = true
                    } else {
                        last = false
                    }

                    row = row_template.replace(
                        /{replace-text}/g,
                        steps[i]['name']
                    )

                    if(last) {
                        if(steps[i]['name'].startsWith("Done")) {
                            button = button_template.replace(
                                /{replace-ip}/g,
                                steps[i]['entries'][0]
                            )
                            
                            $('#installprogress').append(button)
                        } else {
                            row = row.replace(
                                /{replace-done}/g,
                                'info'
                            )   
                            $('#installprogress').append(row)
                        }
                    } else {
                        row_template = row_template.replace(
                            /{replace-done}/g,
                            'success'
                        )
                        $('#installprogress').append(row)
                    }
                }
            }
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