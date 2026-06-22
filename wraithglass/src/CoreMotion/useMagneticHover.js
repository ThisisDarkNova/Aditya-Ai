import { useState, useRef } from 'react';
import { useMotionValue, useSpring } from 'framer-motion';

export function useMagneticHover(pullStrength = 0.5) {
  const ref = useRef(null);
  
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  
  // Spring configuration for that luxurious, heavy feel
  const springX = useSpring(x, { stiffness: 150, damping: 15, mass: 0.5 });
  const springY = useSpring(y, { stiffness: 150, damping: 15, mass: 0.5 });

  const handleMouseMove = (e) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    
    // Calculate distance from center and multiply by pullStrength
    x.set((e.clientX - centerX) * pullStrength);
    y.set((e.clientY - centerY) * pullStrength);
  };

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
  };

  return {
    ref,
    x: springX,
    y: springY,
    handleMouseMove,
    handleMouseLeave
  };
}
