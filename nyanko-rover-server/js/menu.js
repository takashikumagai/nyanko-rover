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

function openLiveFeedAndControl() {
    getLiveFeedAndControl().style.display = 'block';
    getControlTest().style.display = 'none';
    getStatus().style.display = 'none';
    getDebug().style.display = 'none';
}

function openControlTest() {
    getLiveFeedAndControl().style.display = 'none';
    getControlTest().style.display = 'block';
    getStatus().style.display = 'none';
    getDebug().style.display = 'none';
}

function openStatus() {
    getLiveFeedAndControl().style.display = 'none';
    getControlTest().style.display = 'none';
    getStatus().style.display = 'block';
    getDebug().style.display = 'none';

}

function openDeubg() {
    getLiveFeedAndControl().style.display = 'none';
    getControlTest().style.display = 'none';
    getStatus().style.display = 'none';
    getDebug().style.display = 'block';

}

function updateHwStatus() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET','hw-status');
    xhr.load = function() {
        var j = xhr.responseText;
        console.log(j);
        //document.getDocumentById('soc-core-temp').innerHTML = j.temp;
        //document.
    }
    xhr.send();
}
/*
function updateCpuUsage() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET','cpuusage');
    xhr.load = function() {
        document.getDocumentById('cpu-usage').innertHTML = xhr.responseText;
    }
    xhr.send();
}

function updateRamInfo() {
}
*/

function onHwStatusLoaded() {
    console.log("onHwStatusLoaded()");
}

function onHwStatusFailed() {
    console.log("onHwStatusFailed()");
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
