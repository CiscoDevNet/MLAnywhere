$(document).ready(function(){

    $('#consoleLog').append(localStorage.getItem('consoleLog'));

    $('#displayJSON').on('click', function(event) {
        event.preventDefault();      


        $.ajax({
            type: "GET",
            url:"/clusterConfigTemplate",
            dataType: "json",
            success: function (data) {

                $("#jsonModal").modal('show');

                jsonToDisplay = data
                
                form = $("#ccpClusterForm").serializeArray();
                formData = {};

                $(form).each(function(i, field){
                    formData[field.name] = field.value;
                });


                jsonToDisplay["provider_client_config_uuid"] = formData["vsphereProviders"]
                jsonToDisplay["name"] = formData["clusterName"]
                jsonToDisplay["datacenter"] = formData["vsphereDatacenters"]
                jsonToDisplay["cluster"] = formData["vsphereClusters"]
                jsonToDisplay["resource_pool"] = formData["vsphereClusters"] + "/" + formData["vsphereResourcePools"]
                jsonToDisplay["datastore"] = formData["vsphereDatastores"] 
                jsonToDisplay["deployer"]["provider"]["vsphere_client_config_uuid"] = formData["vsphereProviders"] 
                jsonToDisplay["deployer"]["provider"]["vsphere_datacenter"] = formData["vsphereDatacenters"] 
                jsonToDisplay["deployer"]["provider"]["vsphere_datastore"] = formData["vsphereDatastores"] 
                jsonToDisplay["deployer"]["provider"]["vsphere_working_dir"] = "/" + formData["vsphereDatacenters"] + "/vm"
                jsonToDisplay["ingress_vip_pool_id"] = formData["vipPools"] 
                jsonToDisplay["master_node_pool"]["template"] = formData["tenantImageTemplate"] 
                jsonToDisplay["worker_node_pool"]["template"] = formData["tenantImageTemplate"] 
                jsonToDisplay["node_ip_pool_uuid"] = formData["vipPools"] 
                jsonToDisplay["ssh_key"] = formData["sshKey"] 
                jsonToDisplay["networks"] = formData["vsphereNetworks"] 

                $('#jsonModal').find('.modal-body').append('<code><pre style="text-align:justify;">'+JSON.stringify(jsonToDisplay, undefined, 2)+'</pre></code>');
            }
        });
        
     
     });


    
    $('#deployCluster').on('click', function(event) {
        
        event.preventDefault();

        form = $("#ccpClusterForm").serializeArray();
        formData = {};

        $(form).each(function(i, field){
            formData[field.name] = field.value;
        });

        $("#ccpClusterForm :input").prop("disabled", true);

        
        $.ajax({
            url: "/stage2",
            type : "POST",
            contentType: 'application/json',
            dataType : 'json',
            data : JSON.stringify(formData),
            success: function(response) {

                consoleLog = localStorage.getItem('consoleLog');
                consoleLog += $('#consoleLog').val()
                localStorage.setItem('consoleLog', consoleLog);

                $("#ccpClusterForm :input").prop("disabled", false);
                if (response.redirectURL) {
                    window.location.replace(response.redirectURL);
                } else {
                    window.location.reload(true);
                }
            },
            error: function(error) {

                $("#ccpClusterForm :input").prop("disabled", false);
                
                window.location.reload(true);
        }
        });
         
    });
     

     

        
         


})
