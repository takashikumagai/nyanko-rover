var myWebSocket

function parseXml(xmlStr) {
    return new window.DOMParser().parseFromString(xmlStr, "text/xml");
 }

function initWebSocket(serverAddress) {
    console.log("Connecting to a WebSocket server.");
    var wsPort = 9792;
    var serverUrl = "ws://" + serverAddress + ":9792";// + toString(wsPort);
    myWebSocket = new WebSocket(serverUrl);
    myWebSocket.onopen = function(evt) { onWebSocketOpen(evt); };
    myWebSocket.onmessage = function(evt) { onWebSocketMessage(evt); };
    myWebSocket.onerror = function(evt) { onWebSocketError(evt); };
    //myWebSocket.send("ws-nyanko");
    console.log("initWebSocket() leaving.");
}

function onWebSocketOpen(evt) {
    console.log("WebSocket connected.");
}

function onWebSocketMessage(evt) {
    console.log("Message from WebSocket server: " + evt.data);
}

function onWebSocketError(evt) {
    console.log("WebSocket error: " + evt.data);
}

function onServerAddressOrHostnameAcquired(evt) {
    console.log('onServerAddressOrHostnameAcquired');
    console.log(evt.target.responseText);
    serverAddressXml = parseXml(evt.target.responseText);
    nodes = serverAddressXml.getElementsByTagName('nyanko');
    host = nodes[0].innerHTML;
    console.log(host);

    initWebSocket(host);
}

var req = new XMLHttpRequest();
req.open("GET","server_address");
req.addEventListener("load",onServerAddressOrHostnameAcquired);
req.send()

//initWebSocket("localhost");
