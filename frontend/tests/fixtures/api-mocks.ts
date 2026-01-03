/**
 * Mock API responses for frontend tests.
 *
 * All mock data matches the frozen contracts in $lib/types/api.ts.
 */
import type { Project, Container, Workflow, WorkflowExecution } from '$lib/types/api';

export const mockProjects: Project[] = [
  {
    id: 'proj-001',
    name: 'Web App',
    path: '/projects/web-app',
    created_at: '2024-01-15T10:00:00Z',
    container_id: undefined,
    github_url: undefined
  },
  {
    id: 'proj-002',
    name: 'API Service',
    path: '/projects/api-service',
    created_at: '2024-01-16T14:30:00Z',
    container_id: 'container-xyz789',
    github_url: 'https://github.com/user/api-service'
  }
];

export const mockContainers: Container[] = [
  {
    id: 'container-xyz789',
    project_id: 'proj-002',
    status: 'running',
    created_at: '2024-01-16T14:30:00Z',
    image: 'claude-cli:latest'
  }
];

export const mockWorkflows: Workflow[] = [
  {
    id: 'wf-001',
    name: 'TDD Cycle',
    description: 'Test-driven development workflow',
    steps: [
      { name: 'Run Tests', command: 'pytest', review_after: false, timeout_seconds: 300 },
      { name: 'Implement', command: 'claude code', review_after: true, timeout_seconds: 300 },
      { name: 'Refactor', command: 'claude refactor', review_after: true, timeout_seconds: 300 }
    ],
    loop_count: 3,
    max_review_iterations: 5
  }
];

export const mockWorkflowExecutions: WorkflowExecution[] = [
  {
    id: 'exec-001',
    workflow_id: 'wf-001',
    project_id: 'proj-002',
    status: 'running',
    current_step: 1,
    current_loop: 0,
    review_iteration: 2,
    started_at: '2024-01-16T15:00:00Z',
    completed_at: undefined,
    error_message: undefined
  }
];

/**
 * Create a mock fetch that returns predefined responses.
 */
export function createMockFetch(responses: Record<string, unknown>) {
  return async (url: string, options?: RequestInit): Promise<Response> => {
    const path = url.replace(/^.*\/api/, '/api');

    if (path in responses) {
      return new Response(JSON.stringify(responses[path]), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    return new Response(JSON.stringify({ error: 'Not found' }), {
      status: 404,
      headers: { 'Content-Type': 'application/json' }
    });
  };
}

/**
 * Default API responses for common endpoints.
 */
export const defaultApiResponses: Record<string, unknown> = {
  '/api/projects': { projects: mockProjects, total: mockProjects.length },
  '/api/projects/proj-001': mockProjects[0],
  '/api/projects/proj-002': mockProjects[1],
  '/api/containers': { containers: mockContainers, total: mockContainers.length },
  '/api/containers/container-xyz789': mockContainers[0],
  '/api/workflows': { workflows: mockWorkflows, total: mockWorkflows.length },
  '/api/workflows/wf-001': mockWorkflows[0],
  '/api/health': { status: 'healthy', docker_available: true, version: '1.0.0' }
};
