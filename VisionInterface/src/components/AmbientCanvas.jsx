import React, { useEffect, useRef } from 'react';

export default function AmbientCanvas({ activePersona }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    // Mouse coordinates tracker for attraction/repulsion fields
    const mouse = { x: 0, y: 0, active: false };

    // Get neon theme colors based on the persona
    const getPersonaColors = () => {
      switch (activePersona) {
        case 'gamer':
          return ['rgba(168, 85, 247, 0.14)', 'rgba(236, 72, 153, 0.07)']; // Purple, Pink
        case 'streamer':
          return ['rgba(245, 158, 11, 0.14)', 'rgba(239, 68, 68, 0.07)'];  // Orange, Red
        case 'student':
        default:
          return ['rgba(59, 130, 246, 0.14)', 'rgba(16, 185, 129, 0.07)']; // Blue, Green
      }
    };

    const particles = [];
    const particleCount = 28;
    const stars = [];
    const starCount = 60;

    class Particle {
      constructor() {
        this.reset();
      }

      reset() {
        this.x = Math.random() * width;
        this.y = Math.random() * height;
        this.size = Math.random() * 120 + 80;
        this.speedX = (Math.random() - 0.5) * 0.3;
        this.speedY = (Math.random() - 0.5) * 0.3;
        this.alpha = Math.random() * 0.4 + 0.1;
      }

      update() {
        this.x += this.speedX;
        this.y += this.speedY;

        // Interaction with mouse (gentle repulsion)
        if (mouse.active) {
          const dx = this.x - mouse.x;
          const dy = this.y - mouse.y;
          const distance = Math.sqrt(dx * dx + dy * dy);
          const forceRadius = 250;
          if (distance < forceRadius) {
            const force = (forceRadius - distance) / forceRadius;
            const angle = Math.atan2(dy, dx);
            this.x += Math.cos(angle) * force * 1.8;
            this.y += Math.sin(angle) * force * 1.8;
          }
        }

        // Wrap around screen edges smoothly
        if (this.x < -this.size) this.x = width + this.size;
        if (this.x > width + this.size) this.x = -this.size;
        if (this.y < -this.size) this.y = height + this.size;
        if (this.y > height + this.size) this.y = -this.size;
      }

      draw(colors) {
        const gradient = ctx.createRadialGradient(
          this.x,
          this.y,
          0,
          this.x,
          this.y,
          this.size
        );
        gradient.addColorStop(0, colors[0]);
        gradient.addColorStop(0.5, colors[1]);
        gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');

        ctx.beginPath();
        ctx.fillStyle = gradient;
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    // Sparkling Stardust Particle Class
    class Star {
      constructor() {
        this.reset();
      }

      reset() {
        this.x = Math.random() * width;
        this.y = Math.random() * height;
        this.size = Math.random() * 2 + 0.8;
        this.speedX = (Math.random() - 0.5) * 0.12;
        this.speedY = -Math.random() * 0.18 - 0.05; // float upwards gently
        this.maxAlpha = Math.random() * 0.55 + 0.15;
        this.alpha = 0;
        this.twinkleSpeed = Math.random() * 0.008 + 0.003;
        this.twinklingUp = true;
      }

      update() {
        this.x += this.speedX;
        this.y += this.speedY;

        // Twinkle effect
        if (this.twinklingUp) {
          this.alpha += this.twinkleSpeed;
          if (this.alpha >= this.maxAlpha) this.twinklingUp = false;
        } else {
          this.alpha -= this.twinkleSpeed;
          if (this.alpha <= 0.05) this.twinklingUp = true;
        }

        // Gentle mouse repulsion for stars
        if (mouse.active) {
          const dx = this.x - mouse.x;
          const dy = this.y - mouse.y;
          const distance = Math.sqrt(dx * dx + dy * dy);
          const forceRadius = 120;
          if (distance < forceRadius) {
            const force = (forceRadius - distance) / forceRadius;
            const angle = Math.atan2(dy, dx);
            this.x += Math.cos(angle) * force * 1.2;
            this.y += Math.sin(angle) * force * 1.2;
          }
        }

        // Reset if floats off-screen
        if (this.y < 0 || this.x < 0 || this.x > width) {
          this.reset();
          this.y = height;
        }
      }

      draw() {
        ctx.beginPath();
        ctx.fillStyle = `rgba(255, 255, 255, ${this.alpha})`;
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    // Initialize particles & stars
    for (let i = 0; i < particleCount; i++) {
      particles.push(new Particle());
    }
    for (let i = 0; i < starCount; i++) {
      stars.push(new Star());
    }

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };

    const handleMouseMove = (e) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
      mouse.active = true;
    };

    const handleMouseLeave = () => {
      mouse.active = false;
    };

    window.addEventListener('resize', handleResize);
    window.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseleave', handleMouseLeave);

    // Animation Loop
    const render = () => {
      ctx.fillStyle = 'rgba(12, 12, 13, 0.14)'; // Keep trailing frames
      ctx.fillRect(0, 0, width, height);

      // Draw stardust background first
      stars.forEach((s) => {
        s.update();
        s.draw();
      });

      // Draw major ambient orbs
      const colors = getPersonaColors();
      particles.forEach((p) => {
        p.update();
        p.draw(colors);
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, [activePersona]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        zIndex: -1,
        pointerEvents: 'none',
        background: '#0c0c0d',
      }}
    />
  );
}
