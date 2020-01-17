$(document).ready(function(){
    $('#existingClusterUpload').on('click', function(event) {
        event.preventDefault();
        window.location.href = "../existingClusterUpload";
    });

    $('#ccpLogin').on('click', function(event) {
        event.preventDefault();
        window.location.href = "../ccpLogin";
    });
});