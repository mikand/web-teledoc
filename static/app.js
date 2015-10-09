(function(io) {
    var FPS_WEIGHT = 0.1;
    socket = io.connect();

    var canvas = $("#camera_canvas")[0];

    stream = {
        startTime: new Date().getTime(),
        frameCt: 0,
        fps: $("#fps_counter")[0],
        context: canvas.getContext('2d'),
        canvas: canvas,
    };

    socket.on('frame', function ( data ) {
        // Each time we receive an image, request a new one
        socket.emit( 'stream', data.id );

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


    socket.emit('stream', 0);

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

})( io );
