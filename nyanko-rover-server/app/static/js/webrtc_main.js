// Ref: https://github.com/MulletBoy/Raspberry-Pi-FishCam-Demo-Site

// IIFE
(function () {

    let signalObj = null;

    function startPlay() {
        if (signalObj)
            return;

        let hostname = location.hostname;
        //let address = hostname + ':' + (location.port || (location.protocol === 'https:' ? 443 : 80)) + '/webrtc';
        let port = 8090;
        let address = `${hostname}:${port}/stream/webrtc`;
        //let protocol = location.protocol === "https:" ? "wss:" : "ws:";
        let protocol = 'ws:';
        let wsurl = protocol + '//' + address;

        let video = document.getElementById('v');

        signalObj = new signal(wsurl,
            function (stream) {
                console.log('got a stream!');
                video.srcObject = stream;
                video.play();
            },
            function (error) {
                alert(error);
                signalObj = null;
            },
            function () {
                console.log('websocket closed. bye bye!');
                video.srcObject = null;
                signalObj = null;
            },
            function (message) {
                alert(message);
            }
        );
    }

    function stopPlay() {
        if (signalObj) {
            signalObj.hangup();
            signalObj = null;
        } else {
            console.log('!signalObj')
        }
    }

    window.addEventListener('DOMContentLoaded', function () {

        let start = document.getElementById('start-webrtc-streaming');
        if (start) {
            start.addEventListener('click', function (e) {
                startPlay();
            }, false);
        }
        else {
            // auto play if there is no stop button
            startPlay();
        }

        let stop = document.getElementById('stop-webrtc-streaming');
        if (stop) {
            stop.addEventListener('click', function (e) {
                stopPlay();
            }, false);
        }

        // App will call viewPause/viewResume for view status change
        window.viewPause = stopPlay;
        window.viewResume = startPlay;
    });
})();
