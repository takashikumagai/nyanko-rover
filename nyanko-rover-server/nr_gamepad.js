var haveEvents = 'ongamepadconnected' in window;
var controllers = {};

var currentFwdBackAxisValue = 0.0
var currentSteeringAxisValue = 0.0

function connecthandler(e) {
  console.log("Detected a gamepad.")
  addgamepad(e.gamepad);
}

function addgamepad(gamepad) {
  controllers[gamepad.index] = gamepad;

  var d = document.createElement("div");
  d.setAttribute("id", "controller" + gamepad.index);

  var t = document.getElementById("gamepad_id");
  t.innerHTML = gamepad.id;

  var index = document.getElementById("gamepad_index");
  index.innerHTML = ' (index: ' + gamepad.index + ')';

  var button_info = document.getElementById('gamepad_button_info');
  button_info.innerHTML = toString(gamepad.buttons.length) + " buttons";

  // We will display more detailed info on individual buttons if we have to
//   for(var i = 0; i < gamepad.buttons.length; i++) {
//   }

  gamepad_axes = document.getElementById("gamepad_axes");
  var a = document.createElement("div");
  a.id = "axis_info";
  gamepad_axes.appendChild(a);

  for (var i = 0; i < gamepad.axes.length; i++) {
    var p = document.createElement("progress");
    p.className = "axis";
    //p.id = "a" + i;
    // p.setAttribute("max", "2");
    // p.setAttribute("value", "1");
    // p.innerHTML = i;
    // a.appendChild(p);

    var div = document.createElement('div');
    div.className = 'progress';
    div.setAttribute('data-level','50% nyanko');
    var span = document.createElement('span');
    span.className = 'value';
    span.setAttribute('style','width:50%;');
    div.appendChild(span);
    a.appendChild(div)
  }

  // See https://github.com/luser/gamepadtest/blob/master/index.html
//   var start = document.getElementById("start");
//   if (start) {
//     start.style.display = "none";
//   }

//  document.body.appendChild(d);
  requestAnimationFrame(updateStatus);
}

function disconnecthandler(e) {
  removegamepad(e.gamepad);
}

function removegamepad(gamepad) {
  //var d = document.getElementById("controller" + gamepad.index);
  //document.body.removeChild(d);
  delete controllers[gamepad.index];

  var axis_info = document.getElementById("axis_info");
  document.body.removeChild(axis_info);

  var t = document.getElementById("gamepad_id");
  t.innerHTML = "";

  var index = document.getElementById("gamepad_index");
  index.innerHTML = "";
}

function updateStatus() {
  if (!haveEvents) {
    scangamepads();
  }

  var i = 0;
  var j;

  for (j in controllers) {
    var controller = controllers[j];
    // var d = document.getElementById("controller" + j);
    // var buttons = d.getElementsByClassName("button");

    // for (i = 0; i < controller.buttons.length; i++) {
    //   var b = buttons[i];
    //   var val = controller.buttons[i];
    //   var pressed = val == 1.0;
    //   if (typeof(val) == "object") {
    //     pressed = val.pressed;
    //     val = val.value;
    //   }

    //   var pct = Math.round(val * 100) + "%";
    //   b.style.backgroundSize = pct + " " + pct;

    //   if (pressed) {
    //     b.className = "button pressed";
    //   } else {
    //     b.className = "button";
    //   }
    // }

    var gamepad_axes = document.getElementById("gamepad_axes");
    // var axes = gamepad_axes.getElementsByClassName("axis");
    var axes = gamepad_axes.getElementsByClassName('progress');
    for(i = 0; i < controller.axes.length; i++) {
      var a = axes[i];
      a.innerHTML = i + ": " + controller.axes[i].toFixed(4);
      a.setAttribute("value", controller.axes[i] + 1); // Convert range from [-1,1] to [0,2]

      var val = ((controller.axes[i] + 1) * 50.0).toFixed(0);
      a.setAttribute('style','width:' + val + '%;')

      //var val = controller.axes[i] * 100.0;
      //setFwdBackMotorSpeed(val);
    }

    var steeringAxis = 0;
    var fwdBackAxis = 1;

    var fwdBackAxisPolarity = -1; // 1 or -1
    var steeringAxisPolarity = -1; // 1 or -1

    var newValue = controller.axes[fwdBackAxis];
    if( 0.03 < Math.abs(currentFwdBackAxisValue - newValue)
     || (1.0 - Math.abs(newValue)) < 0.001 && 0.001 < 1.0 - Math.abs(currentFwdBackAxisValue) ) {
      console.log("new f/b axis value: " + newValue);
      sign = Math.sign(newValue);
      absVal = Math.abs(newValue); // range [0.0,1.0]
      var margin = 0.15;
      var speed = 0;
    if(absVal <= margin) {
        speed = 0;
      }
      else {
        zero_to_one = (absVal - margin) / (1.0 - margin); // Convert the range of absVal [0.1,1.0] to [0,1]
        speed = zero_to_one * 100.0 * sign;
      }

      // since speed is [-100,100], rounding up to the first decimal would still give us
      // the resolution of 1000 different output levels and that would be sufficient for our purpose.
      speed = speed.toFixed(1) * fwdBackAxisPolarity;
      console.log('setting f/b motor speed to ' + speed);
      setFwdBackMotorSpeed(speed);
      currentFwdBackAxisValue = newValue;
    }

    newValue = controller.axes[steeringAxis];
    if( 0.03 < Math.abs(currentSteeringAxisValue - newValue)
     || (1.0 - Math.abs(newValue)) < 0.001 && 0.001 < 1.0 - Math.abs(currentSteeringAxisValue) ) {
      console.log("new steering axis value: " + newValue);
      sign = Math.sign(newValue);
      absVal = Math.abs(newValue); // range [0.0,1.0]
      var margin = 0.15;
      var steerng = 0;
      if(absVal <= margin) {
        steering = 0;
      }
      else {
        zero_to_one = (absVal - margin) / (1.0 - margin); // Convert the range of absVal [0.1,1.0] to [0,1]
        steering = zero_to_one * 100.0 * sign;
      }

      // since speed is [-100,100], rounding up to the first decimal would still give us
      // the resolution of 1000 different output levels and that would be sufficient for our purpose.
      steering = steering.toFixed(1) * steeringAxisPolarity;
      console.log('setting steering motor to ' + steering);
      setSteering(steering);
      currentSteeringAxisValue = newValue;
    }
  }

  requestAnimationFrame(updateStatus);
}

function scangamepads() {
  var gamepads = navigator.getGamepads ? navigator.getGamepads() : (navigator.webkitGetGamepads ? navigator.webkitGetGamepads() : []);
  for (var i = 0; i < gamepads.length; i++) {
    if (gamepads[i]) {
      if (gamepads[i].index in controllers) {
        controllers[gamepads[i].index] = gamepads[i];
      } else {
        addgamepad(gamepads[i]);
      }
    }
  }
}


window.addEventListener("gamepadconnected", connecthandler);
window.addEventListener("gamepaddisconnected", disconnecthandler);

if (!haveEvents) {
  console.log("Registering a gamepad scan function.")
  setInterval(scangamepads, 500);
}
