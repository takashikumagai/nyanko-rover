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

function getVideoStreamParams() {
  let r = document.querySelector('#video-stream-resolution');
  let dim = r.options[r.selectedIndex].text.split('x');
  let f = document.querySelector('#video-stream-framerate');
  params = {
    resolution: [parseInt(dim[0].trim()), parseInt(dim[1].trim())],
    framerate: parseInt(f.options[f.selectedIndex].text),
    quality: 0
  }
  console.log(`Selected video options: ${JSON.stringify(params)}`);
  return params;
}

async function postCall(url, jsonPayload) {
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(jsonPayload)
  });
  return response;
}

function startVideoStream() {
  document.querySelector('#document-body').style.backgroundImage
  = `/stream.mjpg?${new Date().getTime()}`;
  postCall('/start-video-stream', getVideoStreamParams())
  .then(function(value) {
    console.log('Stream started');
    location.reload();
  });
}

function stopVideoStream() {
  postCall('/stop-video-stream', {})
  .then(function(value) {
    console.log('Stream stopped');

    // Would it be better to hide the last frame by replace the image
    // so that the user can easily see the video streaming is
    // no longer happening?
    //document.querySelector('#document-body').style.backgroundImage
    //= '/static/img/logo.png';
    //location.reload();
});
}

function resetVideoStream() {

  // Changing style.backgroundImage here with unique string does not work

  let t = new Date().getTime();
  postCall('/reset-video-stream', getVideoStreamParams())
  .then(function(value) {
    console.log('Stream reset');
    // This works with src attribute of img tag but
    // not with style.backgroundImage
    //document.querySelector('#document-body').style.backgroundImage
    //= '/stream.mjpg?t=' + t;

    // This will cause the page to load /stream.mjpg again
    // (See the Network tab to confirm this) but of course
    // it also causes the full page reload and it's not smooth.
    location.reload();
  });
}

function closeVideoStream() {
  postCall('/close-video-stream', {})
  .then(function(value) {
    console.log('Stream closed');
  });
}

async function refreshStreamOptionViews() {

  const response = await fetch('/get-video-stream-options', {
    method: 'GET',
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    // Request with GET/HEAD method cannot have body
    //body:
  });

  response.json().then((data) => {
    let w = data.resolution[0];
    let h = data.resolution[1];
    let resolution = document.querySelector(`option[value='_${w}x${h}']`);
    if(resolution) {
        resolution.selected = true;
    }
    let framerate = document.querySelector(`option[value='_${data.framerate}']`);
    if(framerate) {
        framerate.selected = true;
    }
  });

}

window.addEventListener('DOMContentLoaded', async () => {
  await refreshStreamOptionViews();
});

// Check the available camera and set the default camera.
// Note that this code is executed immediately.
// Ref: https://stackoverflow.com/questions/34589488/es6-immediately-invoked-arrow-function
(async () => {
  const response = await fetch('/get-available-camera-types',{
    method: 'GET',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
  });

  response.json().then((data) => {
    if(data.spherical == 'yes') {
      current_camera_device = '360';
    } else if(data.front == 'yes') {
      current_camera_device = 'front';
    } else {
      current_camera_device = 'none';
    }
  });
})()












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