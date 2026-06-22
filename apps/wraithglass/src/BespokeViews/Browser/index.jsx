import React, { useState } from 'react';
import { Globe, ArrowLeft, ArrowRight, RotateCw, Search, ExternalLink } from 'lucide-react';

export default function Browser() {
  const [url, setUrl] = useState('https://github.com/amdarknova-dev/Wraithglass-Ai');
  const [inputUrl, setInputUrl] = useState('https://github.com/amdarknova-dev/Wraithglass-Ai');
  const [history, setHistory] = useState(['https://github.com/amdarknova-dev/Wraithglass-Ai']);
  const [historyIndex, setHistoryIndex] = useState(0);

  const navigateTo = (targetUrl) => {
    let cleanUrl = targetUrl.trim();
    if (!/^https?:\/\//i.test(cleanUrl)) {
      cleanUrl = `https://${cleanUrl}`;
    }
    const newHistory = history.slice(0, historyIndex + 1);
    newHistory.push(cleanUrl);
    setHistory(newHistory);
    setHistoryIndex(newHistory.length - 1);
    setUrl(cleanUrl);
    setInputUrl(cleanUrl);
  };

  const handleGo = (e) => {
    e.preventDefault();
    navigateTo(inputUrl);
  };

  const handleBack = () => {
    if (historyIndex > 0) {
      const prevIndex = historyIndex - 1;
      setHistoryIndex(prevIndex);
      setUrl(history[prevIndex]);
      setInputUrl(history[prevIndex]);
    }
  };

  const handleForward = () => {
    if (historyIndex < history.length - 1) {
      const nextIndex = historyIndex + 1;
      setHistoryIndex(nextIndex);
      setUrl(history[nextIndex]);
      setInputUrl(history[nextIndex]);
    }
  };

  const handleRefresh = () => {
    const frame = document.getElementById('vespera-browser-frame');
    if (frame) {
      frame.src = url;
    }
  };

  const quickLinks = [
    { name: 'GitHub Repo', url: 'https://github.com/amdarknova-dev/Wraithglass-Ai' },
    { name: 'Wraithglass Docs', url: 'http://localhost:7865/docs' },
    { name: 'Command Center', url: 'http://localhost:7865/dashboard' },
    { name: 'Google Search', url: 'https://www.google.com' }
  ];

  return (
    <div className="w-full h-full flex flex-col p-6 text-white bg-transparent font-sans" style={{ backdropFilter: 'blur(30px)' }}>
      {/* Top Glass Navigation Bar */}
      <div className="flex flex-col gap-4 p-4 mb-4 rounded-2xl border border-white/10 bg-white/5 shadow-2xl">
        <div className="flex items-center gap-4">
          <Globe className="w-6 h-6 text-blue-400" />
          <h2 className="text-xl font-serif tracking-wide text-slate-200">Wraithglass Portal Viewer</h2>
        </div>

        <form onSubmit={handleGo} className="flex items-center gap-3">
          {/* Navigation Controls */}
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleBack}
              disabled={historyIndex === 0}
              className="p-2 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 disabled:opacity-40 transition-all duration-200"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={handleForward}
              disabled={historyIndex === history.length - 1}
              className="p-2 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 disabled:opacity-40 transition-all duration-200"
            >
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={handleRefresh}
              className="p-2 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-all duration-200"
            >
              <RotateCw className="w-4 h-4" />
            </button>
          </div>

          {/* Address input */}
          <div className="flex-1 relative">
            <input
              type="text"
              value={inputUrl}
              onChange={(e) => setInputUrl(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-xl bg-black/40 border border-white/10 text-slate-300 font-mono text-sm focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all duration-300"
              placeholder="Enter URL or search term..."
            />
            <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
          </div>

          <button
            type="submit"
            className="px-5 py-2 rounded-xl bg-blue-500 hover:bg-blue-600 border border-blue-400/20 font-medium tracking-wide text-sm transition-all duration-200 flex items-center gap-2"
          >
            Go <ExternalLink className="w-3.5 h-3.5" />
          </button>
        </form>

        {/* Quick Links / Bookmarks */}
        <div className="flex flex-wrap gap-3">
          {quickLinks.map((link, i) => (
            <button
              key={i}
              onClick={() => navigateTo(link.url)}
              className="px-3.5 py-1.5 rounded-lg bg-white/5 border border-white/5 text-xs text-slate-300 hover:bg-white/10 hover:text-white transition-all duration-200"
            >
              {link.name}
            </button>
          ))}
        </div>
      </div>

      {/* Frame Container */}
      <div className="flex-1 w-full rounded-2xl border border-white/10 bg-black/40 overflow-hidden shadow-inner relative min-h-[400px]">
        <iframe
          id="vespera-browser-frame"
          src={url}
          className="w-full h-full border-none bg-black/20"
          title="Browser View"
          sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
        />
      </div>
    </div>
  );
}
