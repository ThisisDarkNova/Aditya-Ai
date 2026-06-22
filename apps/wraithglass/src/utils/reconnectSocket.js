// ─── utils/reconnectSocket.js ───────────────────────────────────────────────
// Smart reconnecting WebSocket connection wrapper for wake/sleep synchronization.

export class ReconnectingSocket {
  constructor(url, protocols = []) {
    this.url = url;
    this.protocols = protocols;
    this.ws = null;
    this.forcedClose = false;
    this.reconnectAttempts = 0;
    this.maxReconnectInterval = 10000;
    
    // Callbacks
    this.onopen = () => {};
    this.onclose = () => {};
    this.onmessage = () => {};
    this.onerror = () => {};
  }

  connect() {
    this.ws = new WebSocket(this.url, this.protocols);
    
    this.ws.onopen = (event) => {
      this.reconnectAttempts = 0;
      this.onopen(event);
    };

    this.ws.onmessage = (event) => {
      this.onmessage(event);
    };

    this.ws.onerror = (event) => {
      this.onerror(event);
    };

    this.ws.onclose = (event) => {
      this.onclose(event);
      if (!this.forcedClose) {
        const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), this.maxReconnectInterval);
        this.reconnectAttempts++;
        setTimeout(() => this.connect(), delay);
      }
    };
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(data);
      return true;
    }
    return false;
  }

  close() {
    this.forcedClose = true;
    if (this.ws) {
      this.ws.close();
    }
  }
}
