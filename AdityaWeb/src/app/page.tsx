'use client';

import { motion, useScroll, useTransform } from 'framer-motion';
import { useRef } from 'react';
import Link from 'next/link';
import { Activity, Shield, Cpu, Maximize, Zap, Eye, Command } from 'lucide-react';

export default function Home() {
  const containerRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"]
  });

  // Parallax calculations
  const heroY = useTransform(scrollYProgress, [0, 0.2], ["0%", "50%"]);
  const heroOpacity = useTransform(scrollYProgress, [0, 0.15], [1, 0]);
  
  const textScale = useTransform(scrollYProgress, [0.1, 0.3], [0.8, 1]);
  const textOpacity = useTransform(scrollYProgress, [0.1, 0.3], [0, 1]);

  return (
    <main ref={containerRef} className="relative min-h-[500vh] w-full bg-[var(--color-midnight)] overflow-clip">
      
      {/* 
        The Core (Abstract Background) 
        A massive glowing gradient orb that shifts as you scroll
      */}
      <motion.div 
        className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] rounded-full blur-[120px] pointer-events-none opacity-30 z-0"
        style={{
          background: 'radial-gradient(circle, var(--color-highlight) 0%, transparent 70%)',
          scale: useTransform(scrollYProgress, [0, 1], [1, 2]),
          rotate: useTransform(scrollYProgress, [0, 1], [0, 90]),
        }}
      />

      {/* --- HERO SECTION --- */}
      <section className="sticky top-0 h-screen w-full flex flex-col items-center justify-center z-10 overflow-hidden">
        <motion.div 
          style={{ y: heroY, opacity: heroOpacity }}
          className="flex flex-col items-center text-center px-6"
        >
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1.5, ease: [0.16, 1, 0.3, 1] }}
            className="w-16 h-16 rounded-full border border-[var(--color-silver)]/20 flex items-center justify-center mb-8 bg-white/5 backdrop-blur-xl"
          >
            <Command className="w-8 h-8 text-[var(--color-silver)]" />
          </motion.div>
          
          <motion.h1 
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1.5, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="text-7xl md:text-9xl font-serif text-white tracking-tighter leading-[0.9]"
          >
            Aditya. <br />
            <span className="text-[var(--color-silver)]/50 italic">Ascended.</span>
          </motion.h1>
          
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 2, delay: 0.8 }}
            className="mt-12 text-lg tracking-[0.3em] uppercase text-gray-500 font-sans"
          >
            Scroll to initiate symbiosis
          </motion.p>
        </motion.div>
      </section>

      {/* --- THE REVEAL SECTION --- */}
      <section className="relative z-20 h-screen w-full flex items-center justify-center px-6">
        <motion.div 
          style={{ scale: textScale, opacity: textOpacity }}
          className="max-w-5xl text-center"
        >
          <h2 className="text-5xl md:text-7xl font-serif text-white leading-tight mb-8">
            Not an assistant.<br/>
            An extension of your central nervous system.
          </h2>
          <p className="text-xl md:text-3xl text-gray-400 font-light max-w-3xl mx-auto leading-relaxed">
            Aditya hooks directly into your hardware. It monitors your heart rate, predicts your keystrokes, and automatically manages your live stream before you even form the thought.
          </p>
        </motion.div>
      </section>

      {/* --- BENTO BOX FEATURES (APPLE TIER) --- */}
      <section className="relative z-20 min-h-screen w-full flex items-center justify-center px-8 py-24">
        <div className="max-w-7xl w-full grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* Large Card 1 */}
          <div className="md:col-span-2 h-[400px] glass-panel apple-hover p-10 flex flex-col justify-end relative overflow-hidden group">
            <div className="absolute top-10 right-10 p-4 rounded-full bg-white/5 backdrop-blur-md border border-white/10 group-hover:bg-white/10 transition-colors duration-500">
              <Eye className="w-8 h-8 text-[var(--color-silver)]" />
            </div>
            <h3 className="text-4xl font-serif text-white mb-4">Code Telepathy.</h3>
            <p className="text-gray-400 text-lg max-w-md">
              Using local webcam analytics, Aditya tracks your pupil dilation. Look at a block of code, and it understands exactly what you want to refactor.
            </p>
          </div>

          {/* Square Card 1 */}
          <div className="h-[400px] glass-panel apple-hover p-10 flex flex-col justify-between">
            <Shield className="w-10 h-10 text-red-400" />
            <div>
              <h3 className="text-2xl font-serif text-white mb-2">Phantom Mode</h3>
              <p className="text-gray-400">
                If OBS or Discord attempts to capture the display, Aditya instantly renders itself invisible. Your advantage remains an absolute secret.
              </p>
            </div>
          </div>

          {/* Square Card 2 */}
          <div className="h-[400px] glass-panel apple-hover p-10 flex flex-col justify-between">
            <Cpu className="w-10 h-10 text-[var(--color-highlight)]" />
            <div>
              <h3 className="text-2xl font-serif text-white mb-2">Thermal Guardian</h3>
              <p className="text-gray-400">
                Hard hooks into the OS motherboard sensors. If junction temps exceed 85°C during intense gameplay, background LLMs are forcefully suspended.
              </p>
            </div>
          </div>

          {/* Large Card 2 */}
          <div className="md:col-span-2 h-[400px] glass-panel apple-hover p-10 flex flex-col justify-between relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-full h-full opacity-10 group-hover:opacity-20 transition-opacity duration-700 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')]" />
            <div className="relative z-10 flex justify-between w-full">
              <Zap className="w-10 h-10 text-yellow-400" />
              <Activity className="w-10 h-10 text-green-400" />
            </div>
            <div className="relative z-10 mt-auto">
              <h3 className="text-4xl font-serif text-white mb-4">The Chauffeur.</h3>
              <p className="text-gray-400 text-lg max-w-xl">
                A relentless background process that talks directly to OBS Websockets. It switches your streaming scenes automatically based on in-game API events and AFK detection.
              </p>
            </div>
          </div>

        </div>
      </section>

      {/* --- FINAL CALL TO ACTION --- */}
      <section className="relative z-20 h-screen w-full flex flex-col items-center justify-center text-center px-6 border-t border-white/5 bg-gradient-to-t from-[var(--color-midnight-light)] to-transparent">
        <h2 className="text-5xl md:text-8xl font-serif text-white mb-8">Ready to Ascend?</h2>
        <div className="flex gap-6 mt-8">
          <Link 
            href="/dashboard"
            className="apple-hover px-10 py-5 rounded-full bg-white text-black font-semibold tracking-wide text-lg flex items-center gap-3"
          >
            Access Dashboard <Maximize className="w-5 h-5" />
          </Link>
          <Link 
            href="/docs"
            className="apple-hover px-10 py-5 rounded-full bg-transparent border border-white/20 text-white font-medium tracking-wide text-lg"
          >
            View Documentation
          </Link>
        </div>
      </section>

    </main>
  );
}
