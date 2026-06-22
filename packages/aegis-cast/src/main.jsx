import React from 'react'
import ReactDOM from 'react-dom/client'
import SubtitlesWidget from './SubtitlesWidget'
import TelemetryWidget from './TelemetryWidget'

// Render both for demonstration
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <div style={{ position: 'relative', width: '100vw', height: '100vh' }}>
      <SubtitlesWidget />
      <div style={{ position: 'absolute', top: 0, right: 0 }}>
        <TelemetryWidget />
      </div>
    </div>
  </React.StrictMode>,
)
