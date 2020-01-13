$(document).ready(function(){
    $('#uploadCluster').on('click', function(event) {
        event.preventDefault();
        window.location.href = "../stage0";
    });

    $('#createCluster').on('click', function(event) {
        event.preventDefault();
        window.location.href = "../stage1";
    });
});