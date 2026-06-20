import React, { useState, useRef, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';

export default function Tooltip({ children, content, position = 'right', delay = 0.3 }) {
  const [isVisible, setIsVisible] = useState(false);
  const timeoutRef = useRef(null);

  const handleMouseEnter = () => {
    timeoutRef.current = setTimeout(() => setIsVisible(true), delay * 1000);
  };

  const handleMouseLeave = () => {
    clearTimeout(timeoutRef.current);
    setIsVisible(false);
  };

  useEffect(() => {
    return () => clearTimeout(timeoutRef.current);
  }, []);

  const getPositionClasses = () => {
    switch (position) {
      case 'right': return 'left-full ml-3 top-1/2 -translate-y-1/2';
      case 'left': return 'right-full mr-3 top-1/2 -translate-y-1/2';
      case 'top': return 'bottom-full mb-3 left-1/2 -translate-x-1/2';
      case 'bottom': return 'top-full mt-3 left-1/2 -translate-x-1/2';
      default: return 'left-full ml-3 top-1/2 -translate-y-1/2';
    }
  };

  const getInitialAnimation = () => {
    switch (position) {
      case 'right': return { opacity: 0, x: -8, scale: 0.92 };
      case 'left': return { opacity: 0, x: 8, scale: 0.92 };
      case 'top': return { opacity: 0, y: 8, scale: 0.92 };
      case 'bottom': return { opacity: 0, y: -8, scale: 0.92 };
      default: return { opacity: 0, x: -8, scale: 0.92 };
    }
  };

  return (
    <div 
      className="relative flex items-center justify-center"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {children}
      <AnimatePresence>
        {isVisible && (
          <motion.div
            initial={getInitialAnimation()}
            animate={{ opacity: 1, x: 0, y: 0, scale: 1 }}
            exit={getInitialAnimation()}
            transition={{ type: 'spring', stiffness: 380, damping: 20 }}
            className={`absolute z-50 px-2.5 py-1.5 rounded-md text-[11px] font-medium tracking-wide whitespace-nowrap bg-[#1a1a1c]/90 border border-white/10 text-[#eae6df] shadow-lg backdrop-blur-md pointer-events-none ${getPositionClasses()}`}
          >
            {content}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
