import * as THREE from 'https://unpkg.com/three@0.155.0/build/three.module.js';
import { OrbitControls } from 'https://unpkg.com/three@0.155.0/examples/jsm/controls/OrbitControls.js';

const params = new URLSearchParams(window.location.search);
let currentShape = (params.get('shape') || 'sphere').toLowerCase();
let currentSize = parseFloat(params.get('size') || '1');

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(5, 5, 5);
scene.add(light);
scene.add(new THREE.AmbientLight(0x404040));

const mat = new THREE.MeshStandardMaterial({ color: 0x156289, metalness: 0.2, roughness: 0.6 });
let mesh = null;

function createMesh(shape, size) {
  if (mesh) {
    scene.remove(mesh);
    mesh.geometry.dispose();
    mesh.material.dispose();
    mesh = null;
  }
  let geom;
  if (shape === 'cube') geom = new THREE.BoxGeometry(size, size, size);
  else if (shape === 'cone') geom = new THREE.ConeGeometry(size, size * 2, 48);
  else if (shape === 'cylinder') geom = new THREE.CylinderGeometry(size, size, size * 2, 48);
  else geom = new THREE.SphereGeometry(size, 48, 32);
  mesh = new THREE.Mesh(geom, mat);
  scene.add(mesh);
}

createMesh(currentShape, currentSize);

camera.position.set(3, 3, 3);
camera.lookAt(0, 0, 0);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// UI bindings
const shapeSelect = document.getElementById('shapeSelect');
const sizeInput = document.getElementById('sizeInput');
if (shapeSelect && sizeInput) {
  shapeSelect.value = currentShape;
  sizeInput.value = String(currentSize);

  function updateFromUI() {
    const s = shapeSelect.value;
    const sz = parseFloat(sizeInput.value) || 1;
    currentShape = s;
    currentSize = sz;
    createMesh(currentShape, currentSize);
    const url = new URL(window.location.href);
    url.searchParams.set('shape', currentShape);
    url.searchParams.set('size', String(currentSize));
    window.history.replaceState({}, '', url.toString());
  }

  shapeSelect.addEventListener('change', updateFromUI);
  sizeInput.addEventListener('change', updateFromUI);
  sizeInput.addEventListener('input', updateFromUI);
}

// Telegram WebApp close button
if (window.Telegram && window.Telegram.WebApp) {
  const btn = document.createElement('button');
  btn.textContent = 'Close';
  btn.className = 'close-btn';
  document.body.appendChild(btn);
  btn.addEventListener('click', () => window.Telegram.WebApp.close());
}
