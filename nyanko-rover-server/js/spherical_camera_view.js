// Dependencies: three.js

// We assume mouse does not have  more than 12 buttons and event.button starts with 0 and increase linearly.
var mouseDown = [0,0,0,0,0,0,0,0,0,0,0,0];

var camera, scene, renderer;
var meshes = [];
var prevClientX = 0, prevClientY = 0;

const canvas2d = document.getElementById('2d');
//canvas2d.width = 1024;
//canvas2d.height = 1024;
const ctx = canvas2d.getContext("2d");

// Render this image to canvas2d above and use canvas2d as the texture for the sphere mesh
const img = new Image();
//img.crossOrigin = 'anonymous' // Commented out; this should be unnecessary as we live stream from the same origin.
img.src = '/stream360.mjpg';

// Test with a static image
//img.src = '/images/dual-fisheye-sample-image.jpg';

const map = new THREE.Texture(canvas2d);
const mjpgMaterial = new THREE.MeshBasicMaterial({ map: map });

/**
 * dir: 1 or -1
 *
 */
function createHemisphereGeometry(radius,dir,cu,cv) {
    let r = radius;

    var geom = new THREE.Geometry(); 

    let points = [];

    let num_z_segments = 16;
    let num_xy_segments = 32;

    let uvs = [];
    let margin = 0.05;
    let ru = 0.25 * (1.0 - margin);
    let rv = 0.5 * (1.0 - margin);;

    let half_pi = Math.PI / 2.0;
    for(let s=0; s<num_z_segments; s++) {
        let zc = (s / num_z_segments) * half_pi;

        for(let t=0; t<num_xy_segments; t++) {

            // angle of rotation on xy plane in radians
            let xyc = (t / num_xy_segments) * (Math.PI * 2.0) * dir;

            let x = Math.cos(xyc) * Math.cos(zc) * r;
            let y = Math.sin(xyc) * Math.cos(zc) * r;
            let z = Math.sin(zc) * r * dir * (-1.0);

            geom.vertices.push(new THREE.Vector3(x,y,z));

            let u = cu + (Math.cos(xyc) * ru * (num_z_segments - s) / num_z_segments) * dir;
            let v = cv +  Math.sin(xyc) * rv * (num_z_segments - s) / num_z_segments;
            uvs.push( new THREE.Vector2(u,v) );
        }
    }

    // Add the last one vertex to close the top of the dome
    geom.vertices.push(new THREE.Vector3(0,0,r * dir * (-1.0)));
    uvs.push( new THREE.Vector2(cu,cv) );

    // Faces (polygon indices)

    for(let s=0; s<num_z_segments-1; s++) {
        for(let t=0; t<num_xy_segments; t++) {
            //let i = ;
            let i0 = s * num_xy_segments + t;
            let i1 = s * num_xy_segments + (t+1) % num_xy_segments;
            let i2 = (s+1) * num_xy_segments + (t+1) % num_xy_segments;
            let i3 = (s+1) * num_xy_segments + t;
            geom.faces.push( new THREE.Face3(i0,i1,i2) );
            geom.faces.push( new THREE.Face3(i0,i2,i3) );

            geom.faceVertexUvs[0].push([ uvs[i0], uvs[i1], uvs[i2] ]);
            geom.faceVertexUvs[0].push([ uvs[i0], uvs[i2], uvs[i3] ]);
        }
    }

    // Close the hole
    let i2 = num_z_segments * num_xy_segments;
    for(let t=0; t<num_xy_segments; t++) {
        let i0 = (num_z_segments-1) * num_xy_segments + t;
        let i1 = (num_z_segments-1) * num_xy_segments + (t+1) % num_xy_segments;
        geom.faces.push( new THREE.Face3(i0,i1,i2) );
        geom.faceVertexUvs[0].push([ uvs[i0], uvs[i1], uvs[i2] ]);
    }

    return geom;
}

function initSphericalView() {

    console.log('initSphericalView')

    camera = new THREE.PerspectiveCamera( 70, window.innerWidth / window.innerHeight, 1, 1000 );
    camera.position.z = 0;

    scene = new THREE.Scene();

    var texture = new THREE.TextureLoader().load( '/js/image.jpg' );

    var hemispheres = [
        createHemisphereGeometry(10.0, 1.0, 0.25, 0.50),
        createHemisphereGeometry(10.0,-1.0, 0.75, 0.50)
    ];

    var material = new THREE.MeshBasicMaterial( { map: texture } );

    for(let i=0; i<2; i++) {
        meshes.push( new THREE.Mesh( hemispheres[i], mjpgMaterial ) );
        meshes[meshes.length-1].scale = THREE.Vector3(2,2,2);
        scene.add( meshes[i] );
    }

    console.log('Creating WebGL renderer')

    renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('3d') });

    //renderer = new THREE.WebGLRenderer( { antialias: true } );
    renderer.setPixelRatio( window.devicePixelRatio );
    renderer.setSize( window.innerWidth, window.innerHeight );
    //document.body.appendChild( renderer.domElement );

    window.addEventListener( 'resize', onWindowResize, false );

    // VR-related settings

    //renderer.vr.enabled = true;
    //
    //window.addEventListener( 'vrdisplaypointerrestricted', onPointerRestricted, false );
    //window.addEventListener( 'vrdisplaypointerunrestricted', onPointerUnrestricted, false );

    //document.body.appendChild( WEBVR.createButton( renderer ) );

}

function onPointerRestricted() {
    var pointerLockElement = renderer.domElement;
    if ( pointerLockElement && typeof(pointerLockElement.requestPointerLock) === 'function' ) {
        pointerLockElement.requestPointerLock();

    }
}

function onPointerUnrestricted() {
    var currentPointerLockElement = document.pointerLockElement;
    var expectedPointerLockElement = renderer.domElement;
    if ( currentPointerLockElement && currentPointerLockElement === expectedPointerLockElement && typeof(document.exitPointerLock) === 'function' ) {
        document.exitPointerLock();
    }
}

function onWindowResize() {

    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();

    renderer.setSize( window.innerWidth, window.innerHeight );

}

function onMouseDown(e) {
    mouseDown[e.button] = true;

    // This ensures that prevClientX and prevClientY and initialized
    // for the first time app is started.
    prevClientX = e.clientX;
    prevClientY = e.clientY;
}

function onMouseUp(e) {
    mouseDown[e.button] = false;
}

function onMouseMove(e) {
    let dx = e.clientX - prevClientX;
    let dy = e.clientY - prevClientY;
    prevClientX = e.clientX;
    prevClientY = e.clientY;

    if(mouseDown[0]) {
        for(let i=0; i<2; i++) {
            meshes[i].rotation.x += dy * 0.008;
            meshes[i].rotation.y += dx * 0.008;
        }
    }
}

function animate() {

    requestAnimationFrame( animate );

    try {

    // Draw the mjpg stream into the context.
    // This updates the texture.
    ctx.drawImage(img, 0, 0, 500, 500);
    map.needsUpdate = true;
} catch(err) {
    console.log('drawImage threw an exception: ' + err.message);

    //resetSphericalCamera();
}

    renderer.render( scene, camera );
}

//function resetSphericalCamera() {
//    var xhr = new XMLHttpRequest();
//    xhr.onload = function() {
//        console.log('Spherical camera was reset.');
//    }
//    xhr.onerror = function() {
//        console.log('Failed to reset spherical camera.');
//    }
//    xhr.open('GET','reset_spherical_camera');
//    xhr.send();
//}

// Create a renderer and initialize a scene with sphere meshes
initSphericalView();

// Start rendering
animate();
