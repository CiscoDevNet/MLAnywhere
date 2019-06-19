$(document).ready(function(){
    
    $('#consoleLog').append(localStorage.getItem('consoleLog'));

    $('#downloadKubeconfig').on('click', function(event) {
        
        $("#downloadKubeconfig").prop("disabled", true);

        event.preventDefault();
        
        window.location.href = location.origin + '/downloadKubeconfig'

        $("#downloadKubeconfig").prop("disabled", false);

         
    });
     

     

        
         


})
