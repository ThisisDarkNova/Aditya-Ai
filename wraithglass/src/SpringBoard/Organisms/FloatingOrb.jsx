import React, { useState, useEffect, useRef } from 'react';
import { motion, useAnimation } from 'framer-motion';

export const FloatingOrb = ({ aiState }) => {
  const [isHovered, setIsHovered] = useState(false);
  const orbRef = useRef(null);
  const controls = useAnimation();

  const getOrbState = () => {
    switch(aiState) {
      case 'thinking': return { scale: 1.2, filter: 'hue-rotate(90deg) drop-shadow(0 0 15px rgba(15,82,186,0.8))' };
      case 'speaking': return { scale: [1, 1.1, 1], filter: 'drop-shadow(0 0 20px rgba(34,197,94,0.6))', transition: { repeat: Infinity, duration: 1.5 } };
      default: return { scale: 1, filter: 'drop-shadow(0 0 10px rgba(255,255,255,0.2))' };
    }
  };

  return (
    <div style={{ position: 'relative', width: '300px', height: '300px' }}>
      {/* SVG Filter for Liquid Physics (Gooey effect) */}
      <svg style={{ position: 'absolute', width: 0, height: 0 }}>
        <defs>
          <filter id="goo">
            <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur" />
            <feColorMatrix in="blur" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 18 -7" result="goo" />
            <feBlend in="SourceGraphic" in2="goo" />
          </filter>
        </defs>
      </svg>

      <motion.div
        ref={orbRef}
        className="orb-container"
        style={{
          width: '300px',
          height: '300px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative',
          filter: 'url(#goo)' // Apply Liquid Physics
        }}
        animate={controls}
        drag
        dragConstraints={{ left: -50, right: 50, top: -50, bottom: 50 }}
        dragElastic={0.2}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => {
          setIsHovered(false);
          controls.start({ x: 0, y: 0, transition: { type: "spring", stiffness: 300, damping: 20 } });
        }}
        onDragEnd={() => {
          controls.start({ x: 0, y: 0, transition: { type: "spring", stiffness: 300, damping: 20 } });
        }}
      >
        <motion.div
          animate={getOrbState()}
          transition={{ type: 'spring', stiffness: 100, damping: 20 }}
          style={{
            width: 60,
            height: 60,
            borderRadius: '50%',
            background: 'radial-gradient(circle at 30% 30%, rgba(255,255,255,0.8), rgba(15,82,186,0.9))',
            boxShadow: 'inset 0 0 20px rgba(0,0,0,0.5)',
            border: '1px solid rgba(255,255,255,0.1)'
          }}
        />
      </motion.div>
    </div>
  );
};

export default FloatingOrb;
