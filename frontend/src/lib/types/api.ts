// TypeScript types - Mirror backend Pydantic models

export interface Project {
	id: string;
	name: string;
	path: string;
	created_at: string;
	container_id?: string;
}

export interface CreateProject {
	name: string;
	path: string;
}

export interface Container {
	id: string;
	project_id: string;
	status: ContainerStatus;
}

export type ContainerStatus = 'created' | 'running' | 'exited' | 'error';

export interface TerminalMessage {
	type: 'output' | 'status' | 'error';
	data?: string;
	state?: ProcessState;
}

export interface TerminalCommand {
	type: 'input' | 'interrupt' | 'resize';
	data?: string;
	cols?: number;
	rows?: number;
}

export type ProcessState = 'running' | 'exited' | 'error';

export interface ApiError {
	detail: string;
	status_code?: number;
}
