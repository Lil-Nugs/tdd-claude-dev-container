/**
 * Shared API types - mirrors backend/app/models/contracts.py exactly.
 * FROZEN after Phase 0. Do not modify without coordination.
 *
 * Generated from: backend/app/models/contracts.py
 * Last sync: 2026-01-03
 */

// =============================================================================
// ENUMS - Define allowed values for type-safe fields
// =============================================================================

/**
 * Status of a Docker container running Claude CLI.
 */
export type ContainerStatus = 'created' | 'running' | 'exited' | 'error';

/**
 * Status of a workflow execution.
 */
export type WorkflowStatus = 'pending' | 'running' | 'paused' | 'completed' | 'failed' | 'cancelled';

/**
 * Type of terminal message for WebSocket communication.
 */
export type TerminalMessageType = 'output' | 'input' | 'system' | 'error';

/**
 * Type of command that can be sent to the terminal.
 */
export type TerminalCommandType = 'input' | 'interrupt' | 'resize';

// =============================================================================
// PROJECT MODELS
// =============================================================================

/**
 * Request model for creating a new project.
 */
export interface CreateProject {
  /** Human-readable project name (1-100 chars) */
  name: string;
  /** Filesystem path to project directory */
  path: string;
  /** Whether to scaffold the project with git, GitHub, and beads */
  scaffold?: boolean;
  /** Whether to create a private GitHub repository */
  github_private?: boolean;
}

/**
 * Full project model with all fields.
 */
export interface Project {
  /** Unique project identifier (UUID) */
  id: string;
  /** Human-readable project name */
  name: string;
  /** Filesystem path to project directory */
  path: string;
  /** Timestamp when project was created (ISO 8601) */
  created_at: string;
  /** ID of associated Docker container, if any */
  container_id?: string | null;
  /** URL of GitHub repository, if created */
  github_url?: string | null;
}

// =============================================================================
// CONTAINER MODELS
// =============================================================================

/**
 * Docker container running Claude CLI for a project.
 */
export interface Container {
  /** Docker container ID */
  id: string;
  /** ID of the project this container serves */
  project_id: string;
  /** Current container status */
  status: ContainerStatus;
  /** Timestamp when container was created (ISO 8601) */
  created_at: string;
  /** Docker image used for the container */
  image: string;
}

// =============================================================================
// TERMINAL/WEBSOCKET MODELS
// =============================================================================

/**
 * Message sent from server to client via WebSocket.
 */
export interface TerminalMessage {
  /** Type of terminal message */
  type: TerminalMessageType;
  /** Message content (output text, system message, etc.) */
  data: string;
  /** When the message was generated (ISO 8601) */
  timestamp: string;
}

/**
 * Command sent from client to server via WebSocket.
 */
export interface TerminalCommand {
  /** Type of command */
  type: TerminalCommandType;
  /** Command payload (input text, resize dimensions, etc.) */
  data?: string | null;
}

/**
 * Terminal resize dimensions.
 */
export interface TerminalResize {
  /** Number of columns (1-500) */
  cols: number;
  /** Number of rows (1-200) */
  rows: number;
}

// =============================================================================
// WORKFLOW MODELS
// =============================================================================

/**
 * A single step in a workflow.
 */
export interface WorkflowStep {
  /** Human-readable step name (1-100 chars) */
  name: string;
  /** Command to execute (may contain {placeholders}) */
  command: string;
  /** Whether to trigger self-review after this step */
  review_after?: boolean;
  /** Maximum time for step execution in seconds (1-3600) */
  timeout_seconds?: number;
}

/**
 * A workflow template defining a sequence of steps.
 */
export interface Workflow {
  /** Unique workflow identifier */
  id: string;
  /** Human-readable workflow name (1-100 chars) */
  name: string;
  /** Workflow description (max 500 chars) */
  description?: string;
  /** Ordered list of steps to execute */
  steps: WorkflowStep[];
  /** Number of times to repeat the workflow (1-100) */
  loop_count?: number;
  /** Maximum self-review iterations before proceeding (1-10) */
  max_review_iterations?: number;
}

/**
 * A running or completed workflow execution.
 */
export interface WorkflowExecution {
  /** Unique execution identifier */
  id: string;
  /** ID of the workflow being executed */
  workflow_id: string;
  /** ID of the project running this workflow */
  project_id: string;
  /** Current execution status */
  status: WorkflowStatus;
  /** Index of currently executing step (0-based) */
  current_step: number;
  /** Current loop iteration (0-based) */
  current_loop: number;
  /** Current review iteration for the current step */
  review_iteration: number;
  /** When execution started (ISO 8601) */
  started_at: string;
  /** When execution completed, if finished (ISO 8601) */
  completed_at?: string | null;
  /** Error message if execution failed */
  error_message?: string | null;
}

// =============================================================================
// API RESPONSE WRAPPERS
// =============================================================================

/**
 * Response model for listing projects.
 */
export interface ProjectList {
  /** List of projects */
  projects: Project[];
  /** Total number of projects */
  total: number;
}

/**
 * Response model for listing containers.
 */
export interface ContainerList {
  /** List of containers */
  containers: Container[];
  /** Total number of containers */
  total: number;
}

/**
 * Response model for listing workflow templates.
 */
export interface WorkflowList {
  /** List of workflow templates */
  workflows: Workflow[];
  /** Total number of workflows */
  total: number;
}

/**
 * Health check response.
 */
export interface HealthCheck {
  /** Overall service health status */
  status: 'healthy' | 'degraded' | 'unhealthy';
  /** Whether Docker daemon is accessible */
  docker_available: boolean;
  /** API version */
  version: string;
}

/**
 * Standard error response.
 */
export interface ErrorResponse {
  /** Error type/code */
  error: string;
  /** Human-readable error message */
  message: string;
  /** Additional error details */
  details?: Record<string, unknown> | null;
}

// =============================================================================
// TYPE GUARDS - Runtime type checking utilities
// =============================================================================

export function isContainerStatus(value: string): value is ContainerStatus {
  return ['created', 'running', 'exited', 'error'].includes(value);
}

export function isWorkflowStatus(value: string): value is WorkflowStatus {
  return ['pending', 'running', 'paused', 'completed', 'failed', 'cancelled'].includes(value);
}

export function isTerminalMessageType(value: string): value is TerminalMessageType {
  return ['output', 'input', 'system', 'error'].includes(value);
}

export function isTerminalCommandType(value: string): value is TerminalCommandType {
  return ['input', 'interrupt', 'resize'].includes(value);
}
