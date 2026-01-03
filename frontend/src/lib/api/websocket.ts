import type { TerminalMessage, TerminalCommand } from '$lib/types/api';

export type WebSocketState = 'connecting' | 'connected' | 'disconnected' | 'error';

export interface WebSocketHandlers {
	onMessage?: (message: TerminalMessage) => void;
	onStateChange?: (state: WebSocketState) => void;
	onRawData?: (data: string) => void;
}

export class TerminalWebSocket {
	private ws: WebSocket | null = null;
	private containerId: string;
	private handlers: WebSocketHandlers;
	private reconnectAttempts = 0;
	private maxReconnectAttempts = 5;
	private reconnectDelay = 1000;
	private state: WebSocketState = 'disconnected';

	constructor(containerId: string, handlers: WebSocketHandlers = {}) {
		this.containerId = containerId;
		this.handlers = handlers;
	}

	private getWebSocketUrl(): string {
		const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
		return `${protocol}//${location.host}/api/terminal/${this.containerId}`;
	}

	private setState(newState: WebSocketState): void {
		this.state = newState;
		this.handlers.onStateChange?.(newState);
	}

	connect(): void {
		if (this.ws && this.ws.readyState === WebSocket.OPEN) {
			return;
		}

		this.setState('connecting');
		this.ws = new WebSocket(this.getWebSocketUrl());

		this.ws.onopen = () => {
			this.setState('connected');
			this.reconnectAttempts = 0;
		};

		this.ws.onmessage = (event) => {
			try {
				const message: TerminalMessage = JSON.parse(event.data);
				this.handlers.onMessage?.(message);
			} catch {
				// Raw data, pass through
				this.handlers.onRawData?.(event.data);
			}
		};

		this.ws.onclose = () => {
			this.setState('disconnected');
			this.attemptReconnect();
		};

		this.ws.onerror = () => {
			this.setState('error');
		};
	}

	private attemptReconnect(): void {
		if (this.reconnectAttempts >= this.maxReconnectAttempts) {
			return;
		}

		this.reconnectAttempts++;
		const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

		setTimeout(() => {
			if (this.state === 'disconnected') {
				this.connect();
			}
		}, delay);
	}

	send(command: TerminalCommand): void {
		if (this.ws && this.ws.readyState === WebSocket.OPEN) {
			this.ws.send(JSON.stringify(command));
		}
	}

	sendInput(data: string): void {
		this.send({ type: 'input', data });
	}

	sendInterrupt(): void {
		this.send({ type: 'interrupt' });
	}

	sendResize(cols: number, rows: number): void {
		this.send({ type: 'resize', cols, rows });
	}

	disconnect(): void {
		this.reconnectAttempts = this.maxReconnectAttempts; // Prevent reconnection
		if (this.ws) {
			this.ws.close();
			this.ws = null;
		}
		this.setState('disconnected');
	}

	reconnect(): void {
		this.reconnectAttempts = 0;
		this.disconnect();
		this.connect();
	}

	getState(): WebSocketState {
		return this.state;
	}

	isConnected(): boolean {
		return this.state === 'connected';
	}
}

// Factory function for creating terminal connections
export function createTerminalConnection(
	containerId: string,
	handlers: WebSocketHandlers = {}
): TerminalWebSocket {
	return new TerminalWebSocket(containerId, handlers);
}
