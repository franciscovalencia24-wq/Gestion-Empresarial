// Añadir un sutil efecto de parallax a los "orbs" cuando el usuario mueve el ratón
document.addEventListener('mousemove', (e) => {
    const orbs = document.querySelectorAll('.glow-orb');
    const x = e.clientX / window.innerWidth;
    const y = e.clientY / window.innerHeight;

    orbs.forEach((orb, index) => {
        const speed = index === 0 ? 30 : -30;
        orb.style.transform = `translate(${x * speed}px, ${y * speed}px)`;
    });
});

// Cambiar el estilo del header al hacer scroll
window.addEventListener('scroll', () => {
    const header = document.querySelector('.glass-header');
    if (window.scrollY > 50) {
        header.style.background = 'rgba(3, 7, 18, 0.8)';
        header.style.boxShadow = '0 4px 30px rgba(0, 0, 0, 0.5)';
    } else {
        header.style.background = 'rgba(3, 7, 18, 0.4)';
        header.style.boxShadow = 'none';
    }
});
