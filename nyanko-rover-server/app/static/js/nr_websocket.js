var myWebSocket = null

function parseXml(xmlStr) {
    return new window.DOMParser().parseFromString(xmlStr, "text/xml");
 }

function initWebSocket() {
    console.log("Connecting to a WebSocket server.");
    var wsPort = 9792;
    //var serverUrl = "ws://" + serverAddress + ":9792";// + toString(wsPort);
    var serverUrl = "ws://" + window.location.hostname + ":9792";
    console.log("ws url: " + serverUrl);
    myWebSocket = new WebSocket(serverUrl);
    myWebSocket.onopen = function(evt) { onWebSocketOpen(evt); };
    myWebSocket.onmessage = function(evt) { onWebSocketMessage(evt); };
    myWebSocket.onerror = function(evt) { onWebSocketError(evt); };
    myWebSocket.onclose = function(evt) { onWebSocketClose(evt); };
    //myWebSocket.send("ws-nyanko");
    console.log("initWebSocket() leaving.");
}

function onWebSocketOpen(evt) {
    console.log("WebSocket connected.");
}

function onWebSocketMessage(evt) {
    console.log("Message from WebSocket server: " + evt.data);

    if(1 <= evt.data.length && evt.data[0] == '#') {
        let info = JSON.parse(evt.data.substring(1));
        document.getElementById('network_info').innerHTML = ' - ' + info.ssid + ' (signal strength: ' + info.signal_strength + '/100)';
    }
    else {
        document.getElementById('network_info').innerHTML = ' - ???';
    }
}

function onWebSocketError(evt) {
    console.log("WebSocket error: " + evt.data);
}

function onWebSocketClose(evt) {
    console.log("WebSocket close: " + evt.data);
}

function onServerAddressOrHostnameAcquired(evt) {
    console.log('onServerAddressOrHostnameAcquired');
    console.log(evt.target.responseText);
    serverAddressXml = parseXml(evt.target.responseText);
    let nodes = serverAddressXml.getElementsByTagName('nyanko');
    console.log(nodes);
    if(nodes.length == 0) {
        return
    }
    let host = nodes[0].innerHTML;
    console.log(host);

    initWebSocket(host);
}


initWebSocket();
