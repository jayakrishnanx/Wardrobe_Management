document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('three-bg');
    if (!container) return;

    // SCENE SETUP
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x000000, 0.001); // Pure black fog for depth

    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 1, 10000);
    camera.position.z = 1000;

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    // Styling
    container.style.position = 'fixed';
    container.style.top = '0';
    container.style.left = '0';
    container.style.width = '100%';
    container.style.height = '100%';
    container.style.zIndex = '-1';
    container.style.pointerEvents = 'none';

    // PARTICLES - SIMPLE DOTS
    const particleGeometry = new THREE.BufferGeometry();
    const particleCount = 2000; // Lots of dots

    const posArray = new Float32Array(particleCount * 3);
    const scaleArray = new Float32Array(particleCount);

    for (let i = 0; i < particleCount * 3; i += 3) {
        // Random positions usually Spread out
        posArray[i] = (Math.random() - 0.5) * 4000;     // x
        posArray[i + 1] = (Math.random() - 0.5) * 4000;   // y
        posArray[i + 2] = (Math.random() - 0.5) * 4000;   // z

        // Random scales
        scaleArray[i / 3] = Math.random();
    }

    particleGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
    particleGeometry.setAttribute('aScale', new THREE.BufferAttribute(scaleArray, 1));

    // Custom Shader Material for glowy dots
    // Or simple PointsMaterial
    const material = new THREE.PointsMaterial({
        size: 6,
        color: 0xffffff,
        transparent: true,
        opacity: 0.8,
        map: new THREE.TextureLoader().load('https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/sprites/disc.png'),
        blending: THREE.AdditiveBlending,
        depthWrite: false
    });

    const particlesMesh = new THREE.Points(particleGeometry, material);
    scene.add(particlesMesh);

    // MOUSE
    let mouseX = 0;
    let mouseY = 0;

    document.addEventListener('mousemove', (event) => {
        mouseX = event.clientX - window.innerWidth / 2;
        mouseY = event.clientY - window.innerHeight / 2;
    });

    // ANIMATION
    function animate() {
        requestAnimationFrame(animate);

        // Constant gentle rotation
        particlesMesh.rotation.y += 0.0005;
        particlesMesh.rotation.x += 0.0002;

        // Subtle mouse influence
        particlesMesh.rotation.y += mouseX * 0.00001;
        particlesMesh.rotation.x += mouseY * 0.00001;

        renderer.render(scene, camera);
    }

    animate();

    // RESIZE
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
});
