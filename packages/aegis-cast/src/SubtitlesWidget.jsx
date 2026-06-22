import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function SubtitlesWidget() {
  const [subtitle, setSubtitle] = useState("");

  useEffect(() => {
    // In reality, this connects to umbracore WebSocket
    // WS.on('message', data => setSubtitle(data.text));
    
    // Mock incoming thoughts
    setTimeout(() => setSubtitle("Calculating optimal engagement vector..."), 2000);
    setTimeout(() => setSubtitle(""), 6000);
  }, []);

  return (
    <div style={{ width: '100vw', height: '100vh', background: 'transparent', display: 'flex', alignItems: 'flex-end', justifyContent: 'center', paddingBottom: '100px' }}>
      <AnimatePresence>
        {subtitle && (
          <motion.div
            initial={{ opacity: 0, y: 20, filter: 'blur(10px)' }}
            animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
            exit={{ opacity: 0, y: -20, filter: 'blur(10px)' }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            style={{
              padding: '16px 32px',
              background: 'rgba(0,0,0,0.4)',
              backdropFilter: 'blur(12px)',
              borderRadius: '24px',
              border: '1px solid rgba(255,255,255,0.1)',
              color: 'white',
              fontFamily: '"Playfair Display", serif',
              fontSize: '28px',
              fontWeight: 500,
              textShadow: '0px 2px 10px rgba(0,0,0,0.8)'
            }}
          >
            <span style={{ opacity: 0.5, marginRight: '10px' }}>Vespera:</span>
            {subtitle}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
