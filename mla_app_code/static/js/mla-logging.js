$(document).ready(function(){
    // Using socketio with flask-socketio for logging output at each stage
    var socket = io.connect();

    socket.on('consoleLog', function(msg) {
        
        $('#consoleLog').append(" - " + msg["loggingType"] + ": " + msg["loggingMessage"]);
        $('#consoleLog').append("\n");

        $('#consoleLog').trigger('change');
    });

    $('#consoleLog').on('change', function(){
        $('#consoleLogButton').delay(100).fadeOut().fadeIn('slow')
    });

})
