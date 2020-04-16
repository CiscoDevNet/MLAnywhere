/*

individual functions for each drop down - can consolidate in the future as it's similar code however for now it's easier to read

*/

// populate dropdowns

function dropdownProviders() {
  $.ajax({
    type: "GET",
    url:"/vsphereProviders",
    dataType: "json",
    success: function (data) {
      $('#vsphereProviders').empty()
      if ($.isArray(data)){  
        
        $.each(data,function(i,obj)
        {
              $('#vsphereProviders').append($("<option></option>").attr("value",obj["uuid"]).text(obj["name"]))
        });
      }
     
    }
  });
}

function dropdownDatacenters(uuid) {
  $.ajax({
    type: "GET",
    url:"/vsphereDatacenters?"+ $.param({ "vsphereProviderUUID":uuid  }),
    dataType: "json",
    success: function (data) {
      $('#vsphereDatacenters').empty()
      if ($.isArray(data)){  
        
        $.each(data,function(i,obj)
        {
              $('#vsphereDatacenters').append($("<option></option>").attr("value",obj).text(obj))
        });
      }
     
    }
  });
}

function dropdownClusters(uuid,datacenter) {
  $.ajax({
    type: "GET",
    url:"/vsphereClusters?"+ $.param({ "vsphereProviderUUID":uuid,"vsphereProviderDatacenter":datacenter  }),
    dataType: "json",
    success: function (data) {
      $('#vsphereClusters').empty()
      if ($.isArray(data)){  
       
        $.each(data,function(i,obj)
        {
              $('#vsphereClusters').append($("<option></option>").attr("value",obj).text(obj))
        });
      }
     
    }
  });
}

function dropdownNetworks(uuid,datacenter) {
  $.ajax({
    type: "GET",
    url:"/vsphereNetworks?"+ $.param({ "vsphereProviderUUID":uuid,"vsphereProviderDatacenter":datacenter  }),
    dataType: "json",
    success: function (data) {
      $('#vsphereNetworks').empty()  
      if ($.isArray(data)){     
         
        $.each(data,function(i,obj)
        {
              $('#vsphereNetworks').append($("<option></option>").attr("value",obj).text(obj))
        });
      }
     
    }
  });
}

function dropdownDatastores(uuid,datacenter) {
  $.ajax({
    type: "GET",
    url:"/vsphereDatastores?"+ $.param({ "vsphereProviderUUID":uuid,"vsphereProviderDatacenter":datacenter  }),
    dataType: "json",
    success: function (data) {
      $('#vsphereDatastores').empty()
      if ($.isArray(data)){  
        
        $.each(data,function(i,obj)
        {
              $('#vsphereDatastores').append($("<option></option>").attr("value",obj).text(obj))
        });

      }
     
    }
  });
}

function dropdownGPUs(uuid,datacenter,cluster) {
  $.ajax({
    type: "GET",
    url:"/gpus?"+ $.param({ "vsphereProviderUUID":uuid,"vsphereProviderDatacenter":datacenter, "vsphereProviderCluster":cluster  }),
    dataType: "json",
    success: function (data) {
      $('#gpus').empty()
      if ($.isArray(data)){  
       
        $.each(data,function(i,obj)
        {
              $('#gpus').append($("<option></option>").attr("value",obj).text(obj))
        });

      }
     

    },
    error: function(XMLHttpRequest, textStatus, errorThrown) { 
      alert("Status: " + textStatus); alert("Error: " + errorThrown); 
    } 

  });
}

function dropdownTemplates(uuid,datacenter) {

  $.ajax({
    type: "GET",
    url:"/vsphereVMs?"+ $.param({ "vsphereProviderUUID":uuid,"vsphereProviderDatacenter":datacenter  }),
    dataType: "json",
    success: function (data) {
      $('#tenantImageTemplate').empty()
      if ($.isArray(data)){  
       
        $.each(data,function(i,obj)
        {
              $('#tenantImageTemplate').append($("<option></option>").attr("value",obj).text(obj))
        });
      }
     
    }
  });
}

function dropdownResourcePools(uuid,datacenter,cluster) {
  $.ajax({
    type: "GET",
    url:"/vsphereResourcePools?"+ $.param({ "vsphereProviderUUID":uuid,"vsphereProviderDatacenter":datacenter,"vsphereProviderCluster":cluster  }),
    dataType: "json",
    success: function (data) {
      $('#vsphereResourcePools').empty()
      if ($.isArray(data)){  
        $.each(data,function(i,obj)
        {
              $('#vsphereResourcePools').append($("<option></option>").attr("value",obj).text(obj))
        });
      }
     
    }
  });
}

function dropdownVIPPools(uuid,datacenter,cluster) {
  $.ajax({
    type: "GET",
    url:"/vipPools",
    dataType: "json",
    success: function (data) {

      $('#vipPools').empty()
      if ($.isArray(data)){  
       
        $.each(data,function(i,obj)
        {
              $('#vipPools').append($("<option></option>").attr("value",obj["uuid"]).text(obj["name"] + " ("+ obj["free_ips"] + " free IPs in pool)"))
        });
      }
     
    }
  });
}

$(document).ready(function(){

  $("#vsphereProviders").on("change", function(event){

    
    dropdownDatacenters($('#vsphereProviders').val())
    
      // if there's only a single datacenter then the "on change" event won't happen so we need to trigger it manually
      // need to set a timeout for a small delay otherwise it triggers before the dropdown has had a chance to populate
      setTimeout(function(){ 
        if ($('#vsphereDatacenters').has('option').length == 1){
          $('#vsphereDatacenters').trigger('change');
        }
      }, 1000);

  
   

  });

  $("#vsphereDatacenters").on("change", function(event){

    dropdownClusters($('#vsphereProviders').val(),$('#vsphereDatacenters').val())

      // if there's only a single cluster then the "on change" event won't happen so we need to trigger it manually
      // need to set a timeout for a small delay otherwise it triggers before the dropdown has had a chance to populate
      setTimeout(function(){ 
        if ($('#vsphereClusters').has('option').length == 1){
          $('#vsphereClusters').trigger('change');
        }
      }, 1000);
    
    

  });

  $("#vsphereClusters").on("change", function(event){

    dropdownResourcePools($('#vsphereProviders').val(),$('#vsphereDatacenters').val(),$('#vsphereClusters').val())

    dropdownNetworks($('#vsphereProviders').val(),$('#vsphereDatacenters').val())

    dropdownDatastores($('#vsphereProviders').val(),$('#vsphereDatacenters').val())

    dropdownGPUs($('#vsphereProviders').val(),$('#vsphereDatacenters').val(),$('#vsphereClusters').val())

    dropdownTemplates($('#vsphereProviders').val(),$('#vsphereDatacenters').val())


  });

  $("#proxySwitch").on("change", function(event){

    if ( $("#proxySwitch").is(':checked') ) {
      $( "#proxyInput" ).prop( "disabled", false );
    } 
    else {
      $( "#proxyInput" ).prop( "disabled", true );
    }

  });


  /*

  vsphereProviders dropdown should be the first to be populated so do this on document ready. 
  first checking if it has already been populated
  */

 dropdownProviders()

    // if there's only a single provider then the "on change" event won't happen so we need to trigger it manually
    // need to set a timeout for a small delay otherwise it triggers before the dropdown has had a chance to populate
    setTimeout(function(){ 
      if ($('#vsphereProviders').has('option').length == 1){
        $('#vsphereProviders').trigger('change');
      }
    }, 1000);
    
    


  dropdownVIPPools()

});



