$(document).ready(function(){
    $('#uploadCluster').on('click', function(event) {
        event.preventDefault();
        window.location.href = "../uploadCluster";
    });

    $('#createCluster').on('click', function(event) {
        event.preventDefault();
        window.location.href = "../stage1";
    });
});