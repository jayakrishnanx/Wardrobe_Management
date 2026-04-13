/**
 * CREATIVE 3D BACKGROUND: Interactive Fashion Cards
 * Each card is a 3D object that tilts and reacts to the mouse pointer.
 */

document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('three-bg');
    if (!container) return;

    // SCENE SETUP
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xF5FBE6);
    scene.fog = new THREE.FogExp2(0xF5FBE6, 0.0008);

    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 1, 10000);
    camera.position.z = 1200;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    // Global Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0xffffff, 0.5);
    pointLight.position.set(500, 500, 500);
    scene.add(pointLight);

    // Styling
    container.style.position = 'fixed';
    container.style.top = '0';
    container.style.left = '0';
    container.style.width = '100%';
    container.style.height = '100%';
    container.style.zIndex = '-1';
    container.style.pointerEvents = 'none';

    // ASSETS
    const textureLoader = new THREE.TextureLoader();
    const textures = [
        textureLoader.load('/static/assets/icons/dress.png'),
        textureLoader.load('/static/assets/icons/tuxedo.png'),
        textureLoader.load('/static/assets/icons/hanger.png')
    ];

    // CREATE FASHION CARDS
    const cards = [];
    const cardCount = 15;

    for (let i = 0; i < cardCount; i++) {
        const group = new THREE.Group();

        // Card Dimensions
        const width = 280;
        const height = 380;

        // Front Face (Icon)
        const texture = textures[Math.floor(Math.random() * textures.length)];
        const frontMaterial = new THREE.MeshBasicMaterial({ 
            map: texture, 
            transparent: true, 
            side: THREE.FrontSide,
            blending: THREE.MultiplyBlending // Makes white backgrounds invisible on the white card
        });
        const frontPlane = new THREE.Mesh(new THREE.PlaneGeometry(width, height), frontMaterial);
        
        // Back/Base (Paper effect)
        const backMaterial = new THREE.MeshPhongMaterial({ 
            color: 0x233D4D, 
            side: THREE.DoubleSide,
            shininess: 30
        });
        const backPlane = new THREE.Mesh(new THREE.PlaneGeometry(width + 10, height + 10), backMaterial);
        backPlane.position.z = -2; // Slightly behind

        group.add(frontPlane);
        group.add(backPlane);

        // Random Initial Position
        group.position.set(
            (Math.random() - 0.5) * 4000,
            (Math.random() - 0.5) * 2000,
            (Math.random() - 0.5) * 1500
        );

        // User Data for Animation
        group.userData = {
            basePosition: group.position.clone(),
            phase: Math.random() * Math.PI * 2,
            floatSpeed: 0.002 + Math.random() * 0.005, // Slower float
            parallaxFactor: 0.05 + Math.random() * 0.1,
            rotationFactor: 1 + Math.random() * 2
        };

        scene.add(group);
        cards.push(group);
    }

    // MOUSE INTERACTION
    let targetMouseX = 0;
    let targetMouseY = 0;
    let currentMouseX = 0;
    let currentMouseY = 0;

    document.addEventListener('mousemove', (event) => {
        targetMouseX = (event.clientX - window.innerWidth / 2) / (window.innerWidth / 2);
        targetMouseY = (event.clientY - window.innerHeight / 2) / (window.innerHeight / 2);
    });

    // ANIMATION LOOP
    function animate() {
        requestAnimationFrame(animate);

        // Smooth Mouse Smoothing (Lerp)
        currentMouseX += (targetMouseX - currentMouseX) * 0.08;
        currentMouseY += (targetMouseY - currentMouseY) * 0.08;

        const time = Date.now();

        cards.forEach(card => {
            const ud = card.userData;
            
            // 1. Floating Animation (Sine Waves) - Extremely subtle
            card.position.y = ud.basePosition.y + Math.sin(time * ud.floatSpeed + ud.phase) * 5;
            card.position.x = ud.basePosition.x + Math.cos(time * ud.floatSpeed * 0.8 + ud.phase) * 3;

            // 2. Interactive Tilt (Mouse Reactivity)
            // Tilt based on mouse position relative to the center
            const targetRotX = currentMouseY * 0.3 * ud.rotationFactor;
            const targetRotY = currentMouseX * 0.3 * ud.rotationFactor;
            
            card.rotation.x += (targetRotX - card.rotation.x) * 0.05;
            card.rotation.y += (targetRotY - card.rotation.y) * 0.05;

            // 3. Parallax Movement - Very subtle
            card.position.x += currentMouseX * 40 * ud.parallaxFactor;
            card.position.y -= currentMouseY * 40 * ud.parallaxFactor;
        });

        renderer.render(scene, camera);
    }

    animate();

    // RESIZE HANDLING
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
});
