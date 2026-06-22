'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { BookOpen, Terminal, Code2, Server, Download, Settings2, ShieldCheck, Cpu } from 'lucide-react';

export default function Docs() {
  const [activeTab, setActiveTab] = useState<'package' | 'manual' | 'post-install'>('package');

  const sections = [
    { title: "Getting Started", icon: <Terminal className="w-5 h-5" />, desc: "Initialize the Phantom Engine." },
    { title: "Architecture", icon: <Server className="w-5 h-5" />, desc: "Deep dive into the Symbiosis Engine." },
    { title: "VS Code Extension", icon: <Code2 className="w-5 h-5" />, desc: "The Ghost Writer configuration." },
  ];

  return (
    <main className="min-h-screen w-full bg-[#0A0D14] text-white pt-32 px-6 md:px-12 pb-16 font-sans flex flex-col md:flex-row gap-8">
      
      {/* Sidebar */}
      <aside className="w-full md:w-64 md:border-r border-white/10 md:pr-8 flex-shrink-0">
        <h3 className="text-xl font-serif text-slate-300 mb-6 flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-blue-400" /> Documentation
        </h3>
        <nav className="flex flex-row md:flex-col gap-3 overflow-x-auto pb-4 md:pb-0">
          {sections.map((sec, i) => (
            <button 
              key={i} 
              className={`text-left px-3 py-2 rounded-lg text-sm tracking-wide transition-all duration-200 flex items-center gap-3 whitespace-nowrap ${
                i === 0 ? 'bg-white/5 border border-white/10 text-white font-medium' : 'text-slate-400 hover:text-white hover:bg-white/[0.02]'
              }`}
            >
              {sec.icon}
              {sec.title}
            </button>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <section className="flex-1 max-w-4xl">
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
          <h1 className="text-4xl md:text-5xl font-serif tracking-tight mb-4 bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            Getting Started with Aditya
          </h1>
          <p className="text-slate-400 text-base md:text-lg leading-relaxed mb-8">
            Aditya is not a standard AI assistant. It is a Sentient OS woven directly into your hardware, 
            stream software, and code editors. Deploy it locally using our automated installers.
          </p>

          {/* Tab Selector */}
          <div className="flex border-b border-white/10 mb-8 gap-4">
            <button
              onClick={() => setActiveTab('package')}
              className={`pb-4 px-2 text-sm font-semibold relative transition-all duration-200 ${
                activeTab === 'package' ? 'text-blue-400' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Package Managers
              {activeTab === 'package' && (
                <motion.div layoutId="activeTabUnderline" className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500" />
              )}
            </button>
            <button
              onClick={() => setActiveTab('manual')}
              className={`pb-4 px-2 text-sm font-semibold relative transition-all duration-200 ${
                activeTab === 'manual' ? 'text-blue-400' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Manual Setup
              {activeTab === 'manual' && (
                <motion.div layoutId="activeTabUnderline" className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500" />
              )}
            </button>
            <button
              onClick={() => setActiveTab('post-install')}
              className={`pb-4 px-2 text-sm font-semibold relative transition-all duration-200 ${
                activeTab === 'post-install' ? 'text-blue-400' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Post-Installation
              {activeTab === 'post-install' && (
                <motion.div layoutId="activeTabUnderline" className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500" />
              )}
            </button>
          </div>

          {/* Interactive Tab Contents */}
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, x: 10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              transition={{ duration: 0.2 }}
            >
              {activeTab === 'package' && (
                <div className="space-y-6">
                  {/* Chocolatey */}
                  <div className="glass-panel p-6 rounded-2xl border border-white/5 bg-white/[0.01]">
                    <div className="flex items-center gap-3 mb-3">
                      <span className="text-lg">🍫</span>
                      <h3 className="font-mono text-sm font-semibold tracking-wider text-slate-300 uppercase">Chocolatey</h3>
                    </div>
                    <p className="text-slate-400 text-sm mb-4">Install Aditya globally using the Windows package manager.</p>
                    <pre className="bg-black/40 p-4 rounded-xl border border-white/10 text-blue-300 font-mono text-xs md:text-sm overflow-x-auto select-all">
                      choco install aditya
                    </pre>
                  </div>

                  {/* Scoop */}
                  <div className="glass-panel p-6 rounded-2xl border border-white/5 bg-white/[0.01]">
                    <div className="flex items-center gap-3 mb-3">
                      <span className="text-lg">🍦</span>
                      <h3 className="font-mono text-sm font-semibold tracking-wider text-slate-300 uppercase">Scoop</h3>
                    </div>
                    <p className="text-slate-400 text-sm mb-4">Add the extras bucket and install the latest release package.</p>
                    <pre className="bg-black/40 p-4 rounded-xl border border-white/10 text-blue-300 font-mono text-xs md:text-sm overflow-x-auto space-y-1.5 select-all">
                      <div>scoop bucket add extras</div>
                      <div>scoop install extras/aditya</div>
                    </pre>
                  </div>

                  {/* WinGet */}
                  <div className="glass-panel p-6 rounded-2xl border border-white/5 bg-white/[0.01]">
                    <div className="flex items-center gap-3 mb-3">
                      <span className="text-lg">📦</span>
                      <h3 className="font-mono text-sm font-semibold tracking-wider text-slate-300 uppercase">WinGet</h3>
                    </div>
                    <p className="text-slate-400 text-sm mb-4">Official Microsoft CLI Package Manager direct command.</p>
                    <pre className="bg-black/40 p-4 rounded-xl border border-white/10 text-blue-300 font-mono text-xs md:text-sm overflow-x-auto select-all">
                      winget install Aditya.Core
                    </pre>
                  </div>
                </div>
              )}

              {activeTab === 'manual' && (
                <div className="space-y-6">
                  {/* step 1 */}
                  <div className="glass-panel p-6 rounded-2xl border border-white/5 bg-white/[0.01]">
                    <h3 className="text-slate-200 font-serif text-lg mb-2">1. Clone Repository</h3>
                    <p className="text-slate-400 text-sm mb-4">Download the latest source code from GitHub to your workspace.</p>
                    <pre className="bg-black/40 p-4 rounded-xl border border-white/10 text-blue-300 font-mono text-xs md:text-sm overflow-x-auto select-all">
                      git clone https://github.com/DarkNova/Aditya.git
                    </pre>
                  </div>

                  {/* step 2 */}
                  <div className="glass-panel p-6 rounded-2xl border border-white/5 bg-white/[0.01]">
                    <h3 className="text-slate-200 font-serif text-lg mb-2">2. Execute Installer</h3>
                    <p className="text-slate-400 text-sm mb-4">Navigate into the directory and initialize local dependencies & virtual environments.</p>
                    <pre className="bg-black/40 p-4 rounded-xl border border-white/10 text-blue-300 font-mono text-xs md:text-sm overflow-x-auto select-all">
                      cd Aditya && .\install.ps1
                    </pre>
                  </div>

                  {/* step 3 */}
                  <div className="glass-panel p-6 rounded-2xl border border-white/5 bg-white/[0.01]">
                    <h3 className="text-slate-200 font-serif text-lg mb-2">3. Run Aditya Core</h3>
                    <p className="text-slate-400 text-sm mb-4">Start the local server and interface core directly from terminal or launch the built EXE.</p>
                    <pre className="bg-black/40 p-4 rounded-xl border border-white/10 text-blue-300 font-mono text-xs md:text-sm overflow-x-auto select-all">
                      .\Release\AdityaCore.exe
                    </pre>
                  </div>
                </div>
              )}

              {activeTab === 'post-install' && (
                <div className="space-y-6">
                  {/* API Credentials */}
                  <div className="glass-panel p-6 rounded-2xl border border-white/5 bg-white/[0.01]">
                    <div className="flex items-center gap-3 mb-3">
                      <Settings2 className="w-5 h-5 text-blue-400" />
                      <h3 className="text-slate-200 font-serif text-lg">Credentials Setup</h3>
                    </div>
                    <p className="text-slate-400 text-sm mb-4">
                      Create a <code className="text-blue-300 font-mono">.env</code> file inside the root directory and add your Gemini tokens:
                    </p>
                    <pre className="bg-black/40 p-4 rounded-xl border border-white/10 text-slate-300 font-mono text-xs md:text-sm overflow-x-auto space-y-1">
                      <div>GEMINI_API_KEY=your_key_here</div>
                      <div>PROJECT_ID=gemini-starter-project</div>
                    </pre>
                  </div>

                  {/* OBS Websocket connection */}
                  <div className="glass-panel p-6 rounded-2xl border border-white/5 bg-white/[0.01]">
                    <div className="flex items-center gap-3 mb-3">
                      <Cpu className="w-5 h-5 text-indigo-400" />
                      <h3 className="text-slate-200 font-serif text-lg">OBS Telemetry Sync</h3>
                    </div>
                    <p className="text-slate-400 text-sm leading-relaxed">
                      Enable OBS WebSockets in OBS Studio: <code className="text-slate-300 font-mono">Tools &gt; WebSocket Server Settings</code>.
                      Configure port <code className="text-blue-300 font-mono">4455</code> to grant Aditya control over scenes.
                    </p>
                  </div>
                </div>
              )}
            </motion.div>
          </AnimatePresence>

          {/* System Requirements & Notices */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-12">
            <div className="glass-panel p-6 rounded-2xl border border-white/5 bg-white/[0.01] flex flex-col justify-between">
              <div>
                <h3 className="text-slate-200 font-serif text-lg mb-2 flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5 text-blue-400" /> System Prerequisites
                </h3>
                <ul className="text-slate-400 text-xs md:text-sm space-y-2 mt-4 list-disc list-inside">
                  <li>Python 3.11+ (For Phantom Engine)</li>
                  <li>Node.js 20+ (For Bespoke Canvas & Web)</li>
                  <li>OBS Studio 30+ (WebSockets Active)</li>
                  <li>VS Code 1.90+</li>
                </ul>
              </div>
            </div>

            <div className="glass-panel p-6 rounded-2xl border-l-4 border-red-500/50 bg-white/[0.01] flex flex-col justify-between">
              <div>
                <h3 className="text-red-400 font-serif text-lg mb-2">Security Notice</h3>
                <p className="text-slate-400 text-xs md:text-sm leading-relaxed mt-4">
                  When Phantom Mode is armed, Aditya will automatically detect Screen Recording software (e.g., Discord Screen Share) 
                  and instantly drop all UI opacities to 0% to prevent leaking local capabilities.
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      </section>

    </main>
  );
}
