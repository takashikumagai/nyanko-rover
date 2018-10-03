// Possible values: 'front', '360'
var current_camera_device = 'front';


function disableStream() {
  return new Promise((resolve,reject) => {
    var xhr = new XMLHttpRequest();
    xhr.open('GET','/stream?close');
    xhr.onload = function() {
      if(this.status >= 200 && this.status < 300) {
        resolve();
      } else {
        reject();
      }
    };
    xhr.onerror = reject;
    xhr.send();
  });
}

function disable360Stream() {
  return new Promise((resolve,reject) => {
    var xhr = new XMLHttpRequest();
    xhr.open('GET','/stream360?close');
    xhr.onload = function() {
      if(this.status >= 200 && this.status < 300) {
        resolve();
      } else {
        reject();
      }
    };
    xhr.onerror = reject;
    xhr.send();
  });
}

function get_num_available_cameras() {
    return 2;
}

function toggleCameras() {
  if(get_num_available_cameras() < 2) {
    return;
  }

  let doc = document.getElementById('document-body');

  if( current_camera_device == 'front' ) {

    // Commented out: don't disable the streaming by the client because other clients might be watching the feed
    //disableStream().then(function(){
    //  console.log('front camera stream successfully closed. opening 360 camera stream.')
    //  //doc.style.backgroundImage = "url('/stream360.mjpg')";
    //  doc.style.backgroundImage = "url('/bg.jpg')";

    //  document.getElementById('spherical-scene').style.display = "block";

    //  current_camera_device = '360';
    //});

    document.getElementById('spherical-scene').style.display = "block";
    doc.style.backgroundImage = "url('/images/bg.jpg')"; // Stop streaming on the background by setting a blank image.
    current_camera_device = '360';

  }
  else if( current_camera_device == '360' ) {

    // Commented out: see the comment in the if block above.
    //disable360Stream().then(function(){
    //  console.log('360 camera stream successfully closed. opening front camera stream.')
    //  doc.style.backgroundImage = "url('/stream.mjpg')";

    //  document.getElementById('spherical-scene').style.display = "none";

    //  current_camera_device = 'front';
    //});

    doc.style.backgroundImage = "url('/stream.mjpg')";
    document.getElementById('spherical-scene').style.display = "none";
    current_camera_device = 'front';
  }
}

function resetSphericalCamera() {
  return new Promise((resolve,reject) => {
    var xhr = new XMLHttpRequest();
    xhr.open('GET','/reset_device');
    xhr.onload = function() {
      if(this.status >= 200 && this.status < 300) {
        resolve();
      } else {
        reject();
      }
    }
    xhr.onerror = reject;
    xhr.send();
  });
}



















//function enable_live_feed() {
//    let doc = document.getElementById('document-body');
//    doc.style.backgroundImage = '/stream.mjpg';
//}

//function disable_live_feed() {
//    let doc = document.getElementById('document-body');
//    doc.style.backgroundImage = '/images/bg.jpg';
//
//    // In addition to replacing .mjpg resource, we need to send a close request
//    // to tell the server to shutdown the camera 
//    var xhr = new XMLHttpRequest();
//    xhr.onload = function() {
//        console.log('Closed the camera device.')
//    }
//    xhr.onerror = function() {
//        console.log('Failed to close the camera device.')
//    }
//    xhr.open('POST','/stream?close');
//    xhr.send();
//}