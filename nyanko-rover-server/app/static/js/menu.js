function getLiveFeedAndControl() {
    return document.getElementById('live-feed-and-control-page');
}

function getControlTest() {
    return document.getElementById('control-test-page');
}

function getStatus() {
    return document.getElementById('status-page');
}

function getDebug() {
    return document.getElementById('debug-page');
}

function getPinMenu() {
    return document.getElementById('pin-modal');
}

function getShutdown() {
    return document.getElementById('shutdown-modal');
}

function openLiveFeedAndControl() {
    getLiveFeedAndControl().style.display = 'block';
    getControlTest().style.display = 'none';
    getStatus().style.display = 'none';
    getDebug().style.display = 'none';
    getShutdown().style.display = 'none';
    getPinMenu().style.display = 'none';
}

function openControlTest() {
    getLiveFeedAndControl().style.display = 'none';
    getControlTest().style.display = 'block';
    getStatus().style.display = 'none';
    getDebug().style.display = 'none';
    getShutdown().style.display = 'none';
    getPinMenu().style.display = 'none';
}

function openStatus() {
    getLiveFeedAndControl().style.display = 'none';
    getControlTest().style.display = 'none';
    getStatus().style.display = 'block';
    getDebug().style.display = 'none';
    getShutdown().style.display = 'none';
    getPinMenu().style.display = 'none';
}

function openDeubg() {
    getLiveFeedAndControl().style.display = 'none';
    getControlTest().style.display = 'none';
    getStatus().style.display = 'none';
    getDebug().style.display = 'block';
    getShutdown().style.display = 'none';
    getPinMenu().style.display = 'none';
}

function updatePin() {
    var xhr = new XMLHttpRequest();
    xhr.onload = function() {
        console.log('xhr pin response text: '+xhr.responseText);
        let r = JSON.parse(xhr.responseText);
        document.getElementById("guest-pin").innerHTML = r.pin;
    }
    xhr.onerror = function() {
        console.log("Not updating pin");
    }
    xhr.open('GET','/pin?_=' + new Date().getTime());
    xhr.send();
}

function openPinMenu() {
    getLiveFeedAndControl().style.display = 'none';
    getControlTest().style.display = 'none';
    getStatus().style.display = 'none';
    getDebug().style.display = 'none';
    getShutdown().style.display = 'none';
    getPinMenu().style.display = 'block';

    updatePin();

    //let x = document.getElementById("pin-modal-content::before");
}

function closePinMenu() {
    openLiveFeedAndControl();
}

function openShutdown() {
    getLiveFeedAndControl().style.display = 'none';
    getControlTest().style.display = 'none';
    getStatus().style.display = 'none';
    getDebug().style.display = 'none';
    getShutdown().style.display = 'block';
    getPinMenu().style.display = 'none';
}

function closeShutdown() {
    getLiveFeedAndControl().style.display = 'block';
    getControlTest().style.display = 'none';
    getStatus().style.display = 'none';
    getDebug().style.display = 'none';
    getShutdown().style.display = 'none';
    getPinMenu().style.display = 'none';
}

var hwStatus = null;

function updateHwStatusView() {
    console.log('updateHwStatus response: ' + hwStatus.responseText) ;
    let j = JSON.parse(hwStatus.responseText);
    console.log(j);
    document.getElementById('system-uptime').innerHTML = j.uptime;
    document.getElementById('cpu-usage').innerHTML = j.cpu_usage;
    document.getElementById('soc-core-temp').innerHTML = j.temp;
    document.getElementById('camera').innerHTML
    = 'Supported: ' + ((j.camera.supported == 1) ? 'Yes' : 'No')
    + ', Detected: ' + ((j.camera.detected == 1) ? 'Yes' : 'No');
}

function updateHwStatus() {
    console.log('updating HW status');
    hwStatus = new XMLHttpRequest();
    hwStatus.onload = updateHwStatusView;
    hwStatus.onerror = function() {
        console.log("Failed to update HW status");
    }
    hwStatus.open('GET','/hw-status?_=' + new Date().getTime());
    hwStatus.send();
}

function onHwStatusLoaded() {
    console.log("onHwStatusLoaded()");
}

function onHwStatusFailed() {
    console.log("onHwStatusFailed()");
}

//setInterval(updateHwStatus,5000);

function parseMyXml(xmlStr) {
    return new window.DOMParser().parseFromString(xmlStr, "text/xml");
}

//console.log('Setting window.onload function');
//window.onload = function() {
//    console.log('window.onload is running.');
//    var xhr = new XMLHttpRequest();
//    xhr.open('GET','hw-status');
//    xhr.load = function() {alert("hw-status onload");};
//    xhr.onerror = function() {alert("hw-status onerror");};
//    xhr.send();

/*    new Promise( function(resolve,reject) {

        // executor function - these lines of code run immediately, before the Promise constructor returns the created object.
        console.log('Executor is running.');
        var xhr = new XMLHttpRequest();
        xhr.open('GET','hw-status');
        xhr.load = function() {alert("hw-status onload");};
        xhr.onerror = function() {alert("hw-status onerror");};
        //xhr.load = () => onHwStatusLoaded();//resolve(xhr.responseText);
        //xhr.onerror = () => onHwStatusFailed();//reject(xhr.statusText);
        xhr.send();

    }).then(function(msg){
        // on fulfilled
        console.log('onload then.');
        if( false ) {//!msg.camera.detected ) {
            document.getElementById('document-body').className = 'stream-bg';
        } else {
            console.log('The app will display a fallback image instead of live streaming footage.')
            document.getElementById('document-body').className = 'placeholder-bg';
        }
    },function(){
        console.log('on rejected');
        // on rejected
        document.getElementById('document-body').className = 'placeholder-bg';
    });*/
//}
