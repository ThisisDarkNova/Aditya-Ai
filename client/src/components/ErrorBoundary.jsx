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
              width: 56,
              height: 56,
              borderRadius: '50%',
              background: 'rgba(239, 68, 68, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ef4444',
              fontSize: 24,
              fontWeight: 'bold',
              marginBottom: 8
            }}>
              ⚠
            </div>
            <h1 style={{ fontSize: 22, fontWeight: 600, margin: 0 }}>Something went wrong</h1>
            <p style={{ color: 'rgba(255,255,255,0.6)', fontSize: 14, lineHeight: 1.6, margin: 0 }}>
              Aditya encountered an unexpected error rendering the interface.
            </p>
            {this.state.error && (
              <pre style={{
                background: 'rgba(0,0,0,0.3)',
                border: '1px solid rgba(255,255,255,0.08)',
                borderRadius: 8,
                padding: 16,
                fontSize: 11,
                fontFamily: 'monospace',
                color: '#f87171',
                maxHeight: 180,
                width: '100%',
                overflowX: 'auto',
                textAlign: 'left',
                boxSizing: 'border-box'
              }}>
                {this.state.error.toString()}
              </pre>
            )}
            <div style={{ display: 'flex', gap: 12, marginTop: 12 }}>
              <button 
                onClick={this.handleReset}
                className="smooth-transition"
                style={{
                  background: 'var(--color-accent, #3B82F6)',
                  color: '#fff',
                  border: 'none',
                  borderRadius: 8,
                  padding: '10px 24px',
                  fontWeight: 500,
                  fontSize: 14,
                  cursor: 'pointer'
                }}
              >
                Reload Application
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
