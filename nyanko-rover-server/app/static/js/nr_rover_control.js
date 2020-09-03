// Dependencies:
//   nr_websocket.js

// Ref: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
async function postData(url = '', data = {}) {
  const response = await fetch(url, {
    method: 'POST',
    mode: 'cors',
    cache: 'no-cache',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  return response.json(); // parses JSON response into native JavaScript objects
}

function moveForward() {
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.open("GET","forward");
  xmlhttp.send();
}

function moveBackward() {
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.open("GET","backward?duration=3");
  xmlhttp.send();
}

function steerLeft() {
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.open("GET","steer?dir=left");
  xmlhttp.send();
}

function steerRight() {
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.open("GET","steer?dir=right");
  xmlhttp.send();
}

function stop() {
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.open("GET","stop");
  xmlhttp.send();
  //myWebSocket.send("sending message via WebSocket");
}

function takePhoto() {
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.open("GET","take_photo");
  xmlhttp.send();
  //myWebSocket.send("sending message via WebSocket");
}

function switch_on_off_streaming(cb) {
  alert('checkbox: ' + (cb.checked ? 'checked' : 'not checked'));
}

function onFwdBackSliderReleased() {
  console.log('resetting f/b slider')
  document.getElementById('slider-fwd_and_back').value = 0;
  stop();
}

function onSteeringSliderReleased() {
  console.log('resetting steering slider')
  document.getElementById('slider-steering').value = 0;
}

// \param[in] speed [-100,100]
function setFwdBackMotorSpeed(speed) {

  // Round to the fist decimal (this will give us the resolution of 1000 levels of outputs)
  speed = Number.parseFloat(speed).toFixed(1);

  var msg = 'f' + speed.toString();
  console.log("ws msg (f/b): " + msg);
  if(myWebSocket != null && myWebSocket.readyState == WebSocket.OPEN) {
    //console.log("sending speed to websocket server");
    myWebSocket.send(msg);
  }
}

function setSteering(steering) {

  // Round to the fist decimal (this will give us the resolution of 1000 levels of outputs, i.e. [-100.0,100.0])
  steering = Number.parseFloat(steering).toFixed(1);

  var msg = 's' + steering.toString();
  console.log("ws msg (steering): " + msg);
  if(myWebSocket != null && myWebSocket.readyState == WebSocket.OPEN) {
    //console.log("sending steering angle to websocket server");
    myWebSocket.send(msg);
  }
}

async function headlightOnOff() {
  fetch('/headlamp')
  .then(response => response.json())
  .then(async data => {
    const brightnessToSet = (data.brightness == 0.0) ? 1.0 : 0.0;
    console.log(`headlight data.brightness: ${data.brightness}`);
    await postData('/headlamp', {brightness: brightnessToSet});
  });
}