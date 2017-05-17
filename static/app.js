// Movement
var keys = {"up" : false,
            "down" : false,
            "left" : false,
            "right" : false};

var last_command_was_stop = false;

var motorSocket = io.connect();

// RTT estimation
motorSocket.on('rttping', function(data) {
    motorSocket.emit('rttpong', data);
});

$(function(){
    motorSocket.emit('motor', {"direction": "none", "steering" : "none"});
    setInterval(function() {
        var direction = "none";
        var steering = "none";
        if (keys["up"] && !keys["down"]) {
            direction = "fwd";
        }
        if (keys["down"] && !keys["up"]) {
            direction = "bwd";
        }
        if (keys["left"] && !keys["right"]) {
            steering = "left";
        }
        if (keys["right"] && !keys["left"]) {
            steering = "right";
        }

        if ((!last_command_was_stop) || (direction != "none" || steering != "none")) {
            motorSocket.emit("motor", {"direction": direction, "steering" : steering});
            last_command_was_stop = (direction == "none" && steering == "none");
        }
    },50);
});

$(document).keydown(function(e) {
    switch(e.which) {
    case 37: // left
        keys["left"] = true;
        break;

    case 38: // up
        keys["up"] = true;
        break;

    case 39: // right
        keys["right"] = true;
        break;

    case 40: // down
        keys["down"] = true;
        break;

    default: return; // exit this handler for other keys
    }
    e.preventDefault(); // prevent the default action (scroll / move caret)
});

$(document).keyup(function(e) {
    switch(e.which) {
    case 37: // left
        keys["left"] = false;
        break;

    case 38: // up
        keys["up"] = false;
        break;

    case 39: // right
        keys["right"] = false;
        break;

    case 40: // down
        keys["down"] = false;
        break;

    default: return; // exit this handler for other keys
    }
    e.preventDefault(); // prevent the default action (scroll / move caret)
});


// Motors
$(function(){
    $('#motor-up').on('mousedown', function(e) {
        keys["up"] = true;
    });
    $('#motor-up').on('mouseup', function(e) {
        keys["up"] = false;
    });

    $('#motor-down').on('mousedown', function(e) {
        keys["down"] = true
    });
    $('#motor-down').on('mouseup', function(e) {
        keys["down"] = false
    });

    $('#motor-fwdleft').on('mousedown', function(e) {
        keys["left"] = true
        keys["up"] = true
    });
    $('#motor-fwdleft').on('mouseup', function(e) {
        keys["left"] = false
        keys["up"] = false
    });

    $('#motor-fwdright').on('mousedown', function(e) {
        keys["right"] = true
        keys["up"] = true
    });
    $('#motor-fwdright').on('mouseup', function(e) {
        keys["right"] = false
        keys["up"] = false
    });

    $('#motor-bwdleft').on('mousedown', function(e) {
        keys["left"] = true
        keys["down"] = true
    });
    $('#motor-bwdleft').on('mouseup', function(e) {
        keys["left"] = false
        keys["down"] = false
    });

    $('#motor-bwdright').on('mousedown', function(e) {
        keys["right"] = true
        keys["down"] = true
    });
    $('#motor-bwdright').on('mouseup', function(e) {
        keys["right"] = false
        keys["down"] = false
    });
});


$(document).keydown(function(e) {
    switch(e.which) {
    case 13: // enter
    case 32: // space
    case 70: // 'f'
        send_rocket_command("fire");
        break;

    default: return; // exit this handler for other keys
    }
    e.preventDefault(); // prevent the default action (scroll / move caret)
});




// Cameras

function makeStream(io, canvas_id, fps_id, stream_id) {
    stream = {
        id: stream_id,
        startTime: new Date().getTime(),
        frameCt: 0,
        fps: $("#" + fps_id)[0],
        context: $("#" + canvas_id)[0].getContext('2d'),
        canvas: $("#" + canvas_id)[0]
    };

    return stream;
}



function launchStreams(io, streams) {
    socket = io.connect();

    socket.on('frame', function ( data ) {
        // Each time we receive an image, request a new one
        socket.emit('stream', data.id);

        stream = streams[data.id];

        img = new Image();
        img.src = data.raw;

        var ctx = stream.context;

        ctx.drawImage(img, 0, 0, stream.canvas.width, stream.canvas.height);

        var size = 30;
        var lw = 3;
        var cx = stream.canvas.width / 2;
        var cy = stream.canvas.height / 2;

        ctx.beginPath();
        ctx.moveTo(cx + size, cy);
        ctx.lineTo(cx - size, cy);
        ctx.lineWidth = lw;
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(cx, cy + size);
        ctx.lineTo(cx, cy - size);
        ctx.lineWidth = lw;
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(cx, cy, size*2/3, 0, 2 * Math.PI, false);
        ctx.lineWidth = lw;
        ctx.stroke();

        stream.frameCt++;
    });

    for (var k in streams) {
        socket.emit('stream', k);

        stream = streams[k];
        // Update fps (loop)
        setInterval( function () {
            d = new Date().getTime(),
            currentTime = ( d - stream.startTime ) / 1000,
            result = Math.floor( ( stream.frameCt / currentTime ) );

            if ( currentTime > 1 ) {
                stream.startTime = new Date().getTime();
                stream.frameCt = 0;
            }

            stream.fps.innerText = result;
        }, 100 );
    }
}

$(document).ready(function() {
    streams = {
        0 : makeStream(io, "camera_canvas_1", "fps_counter_1", 0),
        1 : makeStream(io, "camera_canvas_2", "fps_counter_2", 1)
    };

    launchStreams(io, streams);
});
