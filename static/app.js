var keys = {"up" : false,
            "down" : false,
            "left" : false,
            "right" : false,
            "rocket-up" : false,
            "rocket-down" : false,
            "rocket-left" : false,
            "rocket-right" : false};

var last_command_was_stop = false;
var rocket_last_command_was_stop = false;

var motorSocket = io.connect();
var rocketSocket = io.connect();
var videoSocket = io.connect();

var currentCamera = 0; // Can be 0 or 1
var stream = {startTime: new Date().getTime(),
              frameCt: 0};
var canvas = null;
var ctx = null;

// RTT estimation
motorSocket.on('rttping', function(data) {
    motorSocket.emit('rttpong', data);
});
rocketSocket.on('rttping', function(data) {
    rocketSocket.emit('rttpong', data);
});

// Streams
var current_img = null;

videoSocket.on('frame', function ( data ) {
    // Each time we receive an image, request a new one for the desired stream
    videoSocket.emit('stream', currentCamera);

    if (data.id == currentCamera) {
	img = new Image();
	img.stream_id = data.id;
	img.onload = function(){
	    stream.frameCt++;
	    if (this.stream_id == currentCamera) {
		current_img = this;
	    }	
	};
	img.onerror = function(e){
	    console.log('Error during loading image:', e);
	};
	img.src = data.raw;
    }
});

function drawImage() {
    if (current_img != null && current_img.stream_id == currentCamera) {
	//ctx.clearRect(0, 0, canvas.width, canvas.height);
	ctx.drawImage(current_img, 0, 0, canvas.width, canvas.height);

	if (currentCamera == 1) {
	    var size = 30;
	    var lw = 3;
	    var cx = canvas.width / 2;
	    var cy = canvas.height / 2;

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
	}
    }
    setTimeout(drawImage, 10);
}

$(function(){
    canvas = $("#video_canvas")[0];
    ctx = canvas.getContext('2d');
    var fps = $("#fps")[0];
    
    videoSocket.emit('stream', currentCamera);

    //Draw image
    drawImage();
    
    // Update fps
    setInterval( function () {
	d = new Date().getTime(),
	currentTime = ( d - stream.startTime ) / 1000,
	result = Math.floor( ( stream.frameCt / currentTime ) );

	if ( currentTime > 1 ) {
            stream.startTime = new Date().getTime();
            stream.frameCt = 0;
	}
	fps.innerText = result;
    }, 500 );
});

// Controls
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

        // Rocket
        var command = "stop";
        if (keys["rocket-up"] + keys["rocket-down"] + keys["rock-left"] + keys["rocket-right"] > 1) {
            command = "stop";
        }
        else if (keys["rocket-up"]) {
            command = "up";
        }
        else if (keys["rocket-down"]) {
            command = "down";
        }
        else if (keys["rocket-left"]) {
            command = "left";
        }
        else if (keys["rocket-right"]) {
            command = "right";
        }
        if ((!rocket_last_command_was_stop) || command != "stop") {
            rocketSocket.emit("rocket", {"command": command});
            rocket_last_command_was_stop = (command == "stop");
        }
    },50);
});


function fire_rocket() {
    rocketSocket.emit("rocket", {"command": "fire"});
}

function switch_camera() {
    currentCamera = (currentCamera + 1) % 2;
}


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

    case 65: //a
	keys["rocket-left"] = true;
	break;
    case 83: //s
	keys["rocket-down"] = true;
	break;
    case 68: //d
	keys["rocket-right"] = true;
	break;
    case 87: //w
	keys["rocket-up"] = true;
	break;
	
    case 13: // enter
    case 32: // space
    case 70: // 'f'
        fire_rocket();
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

    case 65: //a
	keys["rocket-left"] = false;
	break;
    case 83: //s
	keys["rocket-down"] = false;
	break;
    case 68: //d
	keys["rocket-right"] = false;
	break;
    case 87: //w
	keys["rocket-up"] = false;
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


    $('#rocket-up').on('mousedown', function(e) {
        keys["rocket-up"] = true;
    });
    $('#rocket-up').on('mouseup', function(e) {
        keys["rocket-up"] = false;
    });
    $('#rocket-down').on('mousedown', function(e) {
        keys["rocket-down"] = true
    });
    $('#rocket-down').on('mouseup', function(e) {
        keys["rocket-down"] = false
    });
    $('#rocket-left').on('mousedown', function(e) {
        keys["rocket-left"] = true;
    });
    $('#rocket-left').on('mouseup', function(e) {
        keys["rocket-left"] = false;
    });
    $('#rocket-right').on('mousedown', function(e) {
        keys["rocket-right"] = true
    });
    $('#rocket-right').on('mouseup', function(e) {
        keys["rocket-right"] = false
    });
    $('#rocket-fire').on('click', function(e) {
        fire_rocket();
    });

    $('#switch-camera').on('click', function(e) {
        switch_camera();
    });
});
