import React from 'react';
import { logger } from '../utils/logger';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ error, errorInfo });
    logger.error('Unhandled UI exception in component tree:', {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo?.componentStack
    });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    if (this.props.onReset) {
      this.props.onReset();
    } else {
      window.location.reload();
    }
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          height: '100vh',
          width: '100vw',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          background: '#04060d',
          color: '#f3f4f6',
          fontFamily: 'system-ui, -apple-system, sans-serif',
          padding: 24,
          boxSizing: 'border-box',
          textAlign: 'center'
        }}>
          <div className="glass-panel" style={{
            maxWidth: 600,
            padding: '40px 24px',
            border: '1px solid rgba(239, 68, 68, 0.2)',
            boxShadow: '0 0 40px rgba(239, 68, 68, 0.1)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 16
          }}>
            <div style={{
              width: 56, height: 56, borderRadius: '50%',
              background: 'rgba(255, 255, 255, 0.05)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              marginBottom: 8
            }}>
              <span style={{ fontSize: 24, filter: 'grayscale(100%) opacity(70%)' }}>⚙️</span>
            </div>
            <h1 style={{ fontSize: 22, fontWeight: 300, margin: 0, fontFamily: 'var(--font-serif)' }}>Recalibrating...</h1>
            <p style={{ color: 'var(--color-text-secondary)', fontSize: 14, lineHeight: 1.6, margin: 0 }}>
              The system is performing a delicate self-correction. Please wait a moment.
            </p>
            <div style={{ display: 'flex', gap: 12, marginTop: 12 }}>
              <button 
                onClick={this.handleReset}
                className="glass-button smooth-transition"
                style={{
                  padding: '10px 24px',
                  fontWeight: 500,
                  fontSize: 14
                }}
              >
                Resume
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
