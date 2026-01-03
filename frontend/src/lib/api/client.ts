import type { Project, CreateProject, Container, ApiError } from '$lib/types/api';

const API_BASE = '/api';

class ApiClient {
	private async request<T>(path: string, options?: RequestInit): Promise<T> {
		const res = await fetch(`${API_BASE}${path}`, {
			...options,
			headers: {
				'Content-Type': 'application/json',
				...options?.headers
			}
		});

		if (!res.ok) {
			let detail = `HTTP ${res.status}`;
			try {
				const error: ApiError = await res.json();
				detail = error.detail || detail;
			} catch {
				// Use status text if JSON parsing fails
				detail = res.statusText || detail;
			}
			throw new Error(detail);
		}

		return res.json();
	}

	// Projects
	async getProjects(): Promise<Project[]> {
		return this.request<Project[]>('/projects');
	}

	async getProject(id: string): Promise<Project> {
		return this.request<Project>(`/projects/${id}`);
	}

	async createProject(data: CreateProject): Promise<Project> {
		return this.request<Project>('/projects', {
			method: 'POST',
			body: JSON.stringify(data)
		});
	}

	async deleteProject(id: string): Promise<void> {
		await this.request(`/projects/${id}`, {
			method: 'DELETE'
		});
	}

	// Containers
	async getContainer(projectId: string): Promise<Container> {
		return this.request<Container>(`/projects/${projectId}/container`);
	}

	async startContainer(projectId: string): Promise<Container> {
		return this.request<Container>(`/projects/${projectId}/container/start`, {
			method: 'POST'
		});
	}

	async stopContainer(projectId: string): Promise<Container> {
		return this.request<Container>(`/projects/${projectId}/container/stop`, {
			method: 'POST'
		});
	}

	// Health check
	async healthCheck(): Promise<{ status: string }> {
		return this.request<{ status: string }>('/health');
	}
}

// Singleton instance
export const apiClient = new ApiClient();

// Convenience exports for direct imports
export async function getProjects(): Promise<Project[]> {
	return apiClient.getProjects();
}

export async function getProject(id: string): Promise<Project> {
	return apiClient.getProject(id);
}

export async function createProject(data: CreateProject): Promise<Project> {
	return apiClient.createProject(data);
}

export async function deleteProject(id: string): Promise<void> {
	return apiClient.deleteProject(id);
}

export async function startContainer(projectId: string): Promise<Container> {
	return apiClient.startContainer(projectId);
}

export async function stopContainer(projectId: string): Promise<Container> {
	return apiClient.stopContainer(projectId);
}
