/**
 * Mock WebSocket for terminal testing.
 *
 * Provides a controllable WebSocket implementation for testing
 * terminal functionality without real network connections.
 */

export class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  readyState = MockWebSocket.CONNECTING;
  url: string;

  onopen: (() => void) | null = null;
  onmessage: ((event: { data: string }) => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: ((error: Error) => void) | null = null;

  private messageQueue: string[] = [];

  constructor(url: string) {
    this.url = url;
    // Simulate connection delay
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN;
      this.onopen?.();
    }, 10);
  }

  send(data: string): void {
    if (this.readyState !== MockWebSocket.OPEN) {
      throw new Error('WebSocket is not open');
    }
    // Echo back for testing
    const parsed = JSON.parse(data);
    if (parsed.type === 'input') {
      this.simulateMessage({
        type: 'output',
        data: `Echo: ${parsed.data}`
      });
    }
  }

  close(): void {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.();
  }

  /**
   * Simulate receiving a message from server.
   */
  simulateMessage(message: object): void {
    setTimeout(() => {
      this.onmessage?.({ data: JSON.stringify(message) });
    }, 0);
  }

  /**
   * Simulate a stream of output.
   */
  simulateStream(lines: string[], delayMs = 50): void {
    lines.forEach((line, i) => {
      setTimeout(() => {
        this.simulateMessage({ type: 'output', data: line + '\n' });
      }, delayMs * i);
    });
  }

  /**
   * Simulate an error event.
   */
  simulateError(message: string): void {
    setTimeout(() => {
      this.onerror?.(new Error(message));
    }, 0);
  }

  /**
   * Simulate connection close from server.
   */
  simulateClose(): void {
    this.readyState = MockWebSocket.CLOSED;
    setTimeout(() => {
      this.onclose?.();
    }, 0);
  }
}

/**
 * Replace global WebSocket with MockWebSocket for testing.
 */
export function installMockWebSocket(): void {
  (globalThis as unknown as { WebSocket: typeof MockWebSocket }).WebSocket = MockWebSocket;
}

/**
 * Restore original WebSocket (call after tests).
 */
let originalWebSocket: typeof WebSocket | undefined;

export function saveMockWebSocket(): void {
  originalWebSocket = globalThis.WebSocket;
}

export function restoreMockWebSocket(): void {
  if (originalWebSocket) {
    globalThis.WebSocket = originalWebSocket;
  }
}
