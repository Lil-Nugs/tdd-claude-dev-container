<script lang="ts">
	import { Terminal } from 'xterm';
	import { FitAddon } from 'xterm-addon-fit';
	import { WebLinksAddon } from 'xterm-addon-web-links';
	import { onMount, onDestroy } from 'svelte';
	import type { TerminalMessage, TerminalCommand, ProcessState } from '$lib/types/api';
	import 'xterm/css/xterm.css';

	export let containerId: string;

	let terminalEl: HTMLDivElement;
	let terminal: Terminal;
	let fitAddon: FitAddon;
	let ws: WebSocket | null = null;
	let status: ProcessState = 'running';

	function connect() {
		const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
		ws = new WebSocket(`${protocol}//${location.host}/api/terminal/${containerId}`);

		ws.onopen = () => {
			status = 'running';
			terminal.writeln('Connected to container...');
		};

		ws.onmessage = (event) => {
			try {
				const msg: TerminalMessage = JSON.parse(event.data);
				if (msg.type === 'output' && msg.data) {
					terminal.write(msg.data);
				} else if (msg.type === 'status' && msg.state) {
					status = msg.state;
				} else if (msg.type === 'error' && msg.data) {
					terminal.writeln(`\r\n\x1b[31mError: ${msg.data}\x1b[0m`);
					status = 'error';
				}
			} catch {
				// Raw data, write directly
				terminal.write(event.data);
			}
		};

		ws.onclose = () => {
			terminal.writeln('\r\n\x1b[33mConnection closed\x1b[0m');
			status = 'exited';
		};

		ws.onerror = () => {
			terminal.writeln('\r\n\x1b[31mWebSocket error\x1b[0m');
			status = 'error';
		};
	}

	function sendCommand(command: TerminalCommand) {
		if (ws && ws.readyState === WebSocket.OPEN) {
			ws.send(JSON.stringify(command));
		}
	}

	function handleResize() {
		if (fitAddon && terminal) {
			fitAddon.fit();
			sendCommand({
				type: 'resize',
				cols: terminal.cols,
				rows: terminal.rows
			});
		}
	}

	onMount(() => {
		terminal = new Terminal({
			cursorBlink: true,
			fontSize: 14,
			fontFamily: 'Menlo, Monaco, "Courier New", monospace',
			theme: {
				background: '#1a1a1a',
				foreground: '#f0f0f0',
				cursor: '#6366f1',
				selectionBackground: 'rgba(99, 102, 241, 0.3)'
			}
		});

		fitAddon = new FitAddon();
		const webLinksAddon = new WebLinksAddon();

		terminal.loadAddon(fitAddon);
		terminal.loadAddon(webLinksAddon);
		terminal.open(terminalEl);
		fitAddon.fit();

		// Handle user input
		terminal.onData((data) => {
			sendCommand({ type: 'input', data });
		});

		// Handle window resize
		window.addEventListener('resize', handleResize);

		// Connect to WebSocket
		connect();
	});

	onDestroy(() => {
		window.removeEventListener('resize', handleResize);
		if (ws) {
			ws.close();
			ws = null;
		}
		if (terminal) {
			terminal.dispose();
		}
	});

	export function interrupt() {
		sendCommand({ type: 'interrupt' });
	}

	export function reconnect() {
		if (ws) {
			ws.close();
		}
		connect();
	}
</script>

<div class="terminal-container">
	<div class="terminal-header">
		<div data-testid="process-status" class="status {status}">
			{status}
		</div>
		<div class="terminal-actions">
			<button class="btn-secondary" on:click={interrupt} data-testid="interrupt-btn">
				Interrupt (Ctrl+C)
			</button>
			<button class="btn-secondary" on:click={reconnect} data-testid="reconnect-btn">
				Reconnect
			</button>
		</div>
	</div>
	<div bind:this={terminalEl} class="terminal" data-testid="terminal"></div>
</div>

<style>
	.terminal-container {
		display: flex;
		flex-direction: column;
		height: 100%;
		background-color: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--border-radius);
		overflow: hidden;
	}

	.terminal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: var(--spacing-sm) var(--spacing-md);
		background-color: var(--color-bg-secondary);
		border-bottom: 1px solid var(--color-border);
	}

	.terminal-actions {
		display: flex;
		gap: var(--spacing-sm);
	}

	.terminal-actions button {
		font-size: 0.75rem;
		padding: var(--spacing-xs) var(--spacing-sm);
	}

	.terminal {
		flex: 1;
		padding: var(--spacing-sm);
	}

	:global(.terminal .xterm) {
		height: 100%;
	}

	:global(.terminal .xterm-viewport) {
		overflow-y: auto !important;
	}
</style>
