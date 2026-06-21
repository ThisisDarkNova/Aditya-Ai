'use client';

import { motion } from 'framer-motion';
import { BookOpen, Terminal, Code2, Server } from 'lucide-react';

export default function Docs() {
  const sections = [
    { title: "Getting Started", icon: <Terminal className="w-6 h-6" />, desc: "Initialize the Phantom Engine." },
    { title: "Architecture", icon: <Server className="w-6 h-6" />, desc: "Deep dive into the Symbiosis Engine." },
    { title: "VS Code Extension", icon: <Code2 className="w-6 h-6" />, desc: "The Ghost Writer configuration." },
  ];

  return (
    <main className="min-h-screen w-full bg-[var(--color-midnight)] text-white pt-32 px-8 pb-12 font-sans flex">
      
      {/* Sidebar */}
      <aside className="w-64 border-r border-white/10 pr-8 hidden md:block">
        <h3 className="text-xl font-serif text-[var(--color-silver)] mb-6 flex items-center gap-2">
          <BookOpen className="w-5 h-5" /> Documentation
        </h3>
        <nav className="flex flex-col gap-4">
          {sections.map((sec, i) => (
            <button key={i} className="text-left text-gray-400 hover:text-white transition-colors duration-200 text-sm tracking-wide">
              {sec.title}
            </button>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <section className="flex-1 max-w-4xl md:pl-12">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }}>
          <h1 className="text-5xl font-serif mb-6">Introduction to Aditya</h1>
          <p className="text-gray-300 text-lg leading-relaxed mb-8">
            Aditya is not a standard AI assistant. It is a Sentient OS woven directly into your hardware, 
            your stream software, and your code editor. 
          </p>

          <div className="glass-panel p-8 rounded-2xl mb-8">
            <h2 className="text-2xl font-serif mb-4 text-[var(--color-highlight)]">Prerequisites</h2>
            <ul className="list-disc list-inside text-gray-400 space-y-2">
              <li>Python 3.11+ (For Phantom Engine)</li>
              <li>Node.js 20+ (For Bespoke Canvas & Web)</li>
              <li>OBS Studio 30+ (With WebSockets Enabled)</li>
              <li>VS Code 1.90+</li>
            </ul>
          </div>

          <div className="glass-panel p-8 rounded-2xl border-l-4 border-red-500/50">
            <h2 className="text-2xl font-serif mb-4 text-red-400">Security Notice (Phantom Mode)</h2>
            <p className="text-gray-400 leading-relaxed">
              When Phantom Mode is armed, Aditya will automatically detect Screen Recording software (e.g., Discord Screen Share) 
              and instantly drop all UI opacities to 0%. Your Rolls-Royce capabilities remain strictly local and hidden.
            </p>
          </div>
        </motion.div>
      </section>

    </main>
  );
}
