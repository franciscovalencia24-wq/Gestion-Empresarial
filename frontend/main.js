import * as THREE from 'three';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { createIcons, ShieldCheck, TrendingUp, Cpu, Link } from 'lucide';

// Initialize Lucide Icons
createIcons({
  icons: {
    ShieldCheck,
    TrendingUp,
    Cpu,
    Link
  }
});

gsap.registerPlugin(ScrollTrigger);

/**
 * 1. WebGL Background (Three.js) - Altus AI Neural Network / Data Particles
 */
const canvas = document.querySelector('#bg-canvas');
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x0A111F, 0.001); // Fade into background color

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.z = 30;

const renderer = new THREE.WebGLRenderer({
  canvas: canvas,
  alpha: true,
  antialias: true
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);

// Particles geometry
const particlesGeometry = new THREE.BufferGeometry();
const particlesCount = 1500;
const posArray = new Float32Array(particlesCount * 3);

for(let i = 0; i < particlesCount * 3; i++) {
  // Spread particles across a wide area
  posArray[i] = (Math.random() - 0.5) * 100;
}

particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));

// Particle Material (Gold & Teal mix)
const material = new THREE.PointsMaterial({
  size: 0.15,
  color: 0xC5A059,
  transparent: true,
  opacity: 0.8,
  blending: THREE.AdditiveBlending
});

const particlesMesh = new THREE.Points(particlesGeometry, material);
scene.add(particlesMesh);

// Mouse interaction
let mouseX = 0;
let mouseY = 0;

document.addEventListener('mousemove', (event) => {
  mouseX = event.clientX / window.innerWidth - 0.5;
  mouseY = event.clientY / window.innerHeight - 0.5;
});

// Animation Loop
const clock = new THREE.Clock();

const tick = () => {
  const elapsedTime = clock.getElapsedTime();

  // Rotate slowly
  particlesMesh.rotation.y = elapsedTime * 0.05;
  particlesMesh.rotation.x = elapsedTime * 0.02;

  // Mouse parallax
  camera.position.x += (mouseX * 5 - camera.position.x) * 0.05;
  camera.position.y += (-mouseY * 5 - camera.position.y) * 0.05;
  camera.lookAt(scene.position);

  renderer.render(scene, camera);
  window.requestAnimationFrame(tick);
};
tick();

// Handle Resize
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});


/**
 * 2. GSAP Scroll Animations
 */

// Reveal elements on scroll
gsap.utils.toArray('.gsap-reveal').forEach((elem) => {
  gsap.fromTo(elem, 
    { y: 50, opacity: 0 }, 
    {
      y: 0,
      opacity: 1,
      duration: 1,
      ease: "power3.out",
      scrollTrigger: {
        trigger: elem,
        start: "top 85%", // Trigger when top of element hits 85% of viewport
        toggleActions: "play none none reverse"
      }
    }
  );
});

// Number Counter Animation for KPIs
const counters = document.querySelectorAll('.counter');
counters.forEach(counter => {
  const target = parseFloat(counter.getAttribute('data-target'));
  
  ScrollTrigger.create({
    trigger: counter,
    start: "top 90%",
    once: true,
    onEnter: () => {
      gsap.to(counter, {
        innerHTML: target,
        duration: 2,
        ease: "power2.out",
        snap: { innerHTML: 0.1 },
        onUpdate: function() {
          counter.innerHTML = Number(this.targets()[0].innerHTML).toFixed(1);
        }
      });
    }
  });
});

// Navbar Scroll Effect
window.addEventListener('scroll', () => {
  const navbar = document.querySelector('.navbar');
  if (window.scrollY > 50) {
    navbar.classList.add('scrolled');
  } else {
    navbar.classList.remove('scrolled');
  }
});

/**
 * 3. 3D Tilt Effect on Glass Cards (Vanilla JS)
 */
const cards = document.querySelectorAll('.tilt-card');

cards.forEach(card => {
  card.addEventListener('mousemove', (e) => {
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left; // x position within the element
    const y = e.clientY - rect.top;  // y position within the element
    
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    
    const rotateX = ((y - centerY) / centerY) * -10; // Max rotation 10deg
    const rotateY = ((x - centerX) / centerX) * 10;
    
    card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
    
    // Move the glow to follow mouse
    const glow = card.querySelector('.card-glow');
    if(glow) {
      glow.style.transform = `translate(${x}px, ${y}px)`;
    }
  });
  
  card.addEventListener('mouseleave', () => {
    card.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg)`;
  });
});

/**
 * 4. Initialize Charts and Simulators
 */
import { initVolatilityChart } from './js/volatility_chart.js';
import { initSimulator } from './js/simulator.js';

document.addEventListener('DOMContentLoaded', () => {
  initVolatilityChart();
  initSimulator();
});
