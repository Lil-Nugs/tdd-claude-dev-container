<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { getProject, deleteProject, startContainer, stopContainer } from '$lib/api/client';
	import type { Project, Container } from '$lib/types/api';

	let project: Project | null = null;
	let loading = true;
	let error: string | null = null;
	let containerLoading = false;
	let deleteConfirm = false;

	$: projectId = $page.params.id;

	onMount(async () => {
		await loadProject();
	});

	async function loadProject() {
		if (!projectId) {
			error = 'Invalid project ID';
			loading = false;
			return;
		}
		loading = true;
		error = null;
		try {
			project = await getProject(projectId);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load project';
		} finally {
			loading = false;
		}
	}

	async function handleStartContainer() {
		if (!project) return;
		containerLoading = true;
		try {
			const container = await startContainer(project.id);
			project = { ...project, container_id: container.id };
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to start container';
		} finally {
			containerLoading = false;
		}
	}

	async function handleStopContainer() {
		if (!project) return;
		containerLoading = true;
		try {
			await stopContainer(project.id);
			project = { ...project, container_id: undefined };
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to stop container';
		} finally {
			containerLoading = false;
		}
	}

	async function handleDelete() {
		if (!project) return;
		try {
			await deleteProject(project.id);
			goto('/projects');
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to delete project';
		}
	}
</script>

<svelte:head>
	<title>{project?.name || 'Project'} - Claude Dev Container</title>
</svelte:head>

<div class="project-detail">
	{#if loading}
		<div class="loading" data-testid="loading">Loading project...</div>
	{:else if error}
		<div class="error" data-testid="error">
			<p>{error}</p>
			<button class="btn-secondary" on:click={loadProject}>Retry</button>
		</div>
	{:else if project}
		<div class="page-header">
			<div class="header-info">
				<a href="/projects" class="back-link">Projects</a>
				<h1 data-testid="project-name">{project.name}</h1>
			</div>
			<div class="header-actions">
				{#if project.container_id}
					<a
						href="/projects/{project.id}/terminal"
						class="btn-primary"
						data-testid="open-terminal-btn"
					>
						Open Terminal
					</a>
				{/if}
			</div>
		</div>

		<div class="project-info card">
			<h2>Project Details</h2>
			<dl>
				<dt>ID</dt>
				<dd data-testid="project-id">{project.id}</dd>

				<dt>Path</dt>
				<dd data-testid="project-path">{project.path}</dd>

				<dt>Created</dt>
				<dd>{new Date(project.created_at).toLocaleString()}</dd>

				<dt>Container Status</dt>
				<dd>
					{#if project.container_id}
						<span class="status running" data-testid="container-status">Running</span>
					{:else}
						<span class="status created" data-testid="container-status">Not Started</span>
					{/if}
				</dd>
			</dl>
		</div>

		<div class="actions-section card">
			<h2>Container Actions</h2>
			<div class="action-buttons">
				{#if project.container_id}
					<button
						class="btn-secondary"
						on:click={handleStopContainer}
						disabled={containerLoading}
						data-testid="stop-container-btn"
					>
						{containerLoading ? 'Stopping...' : 'Stop Container'}
					</button>
				{:else}
					<button
						class="btn-primary"
						on:click={handleStartContainer}
						disabled={containerLoading}
						data-testid="start-container-btn"
					>
						{containerLoading ? 'Starting...' : 'Start Container'}
					</button>
				{/if}
			</div>
		</div>

		<div class="danger-zone card">
			<h2>Danger Zone</h2>
			{#if deleteConfirm}
				<div class="delete-confirm">
					<p>Are you sure you want to delete this project? This action cannot be undone.</p>
					<div class="confirm-buttons">
						<button class="btn-secondary" on:click={() => (deleteConfirm = false)}>Cancel</button>
						<button class="btn-danger" on:click={handleDelete} data-testid="confirm-delete-btn">
							Yes, Delete Project
						</button>
					</div>
				</div>
			{:else}
				<button
					class="btn-danger"
					on:click={() => (deleteConfirm = true)}
					data-testid="delete-project-btn"
				>
					Delete Project
				</button>
			{/if}
		</div>
	{/if}
</div>

<style>
	.project-detail {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-xl);
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
	}

	.header-info {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-xs);
	}

	.back-link {
		font-size: 0.875rem;
		color: var(--color-text-muted);
	}

	.page-header h1 {
		font-size: 2rem;
	}

	.header-actions {
		display: flex;
		gap: var(--spacing-sm);
	}

	.project-info h2,
	.actions-section h2,
	.danger-zone h2 {
		margin-bottom: var(--spacing-lg);
		font-size: 1.25rem;
	}

	dl {
		display: grid;
		grid-template-columns: auto 1fr;
		gap: var(--spacing-sm) var(--spacing-lg);
	}

	dt {
		font-weight: 500;
		color: var(--color-text-muted);
	}

	dd {
		font-family: 'Monaco', 'Menlo', monospace;
		word-break: break-all;
	}

	.action-buttons {
		display: flex;
		gap: var(--spacing-sm);
	}

	.danger-zone {
		border-color: var(--color-error);
	}

	.danger-zone h2 {
		color: var(--color-error);
	}

	.btn-danger {
		background-color: var(--color-error);
		color: white;
	}

	.btn-danger:hover {
		background-color: #dc2626;
	}

	.delete-confirm {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-md);
	}

	.confirm-buttons {
		display: flex;
		gap: var(--spacing-sm);
	}

	.loading,
	.error {
		text-align: center;
		padding: var(--spacing-xl);
	}

	.error {
		color: var(--color-error);
	}

	.error p {
		margin-bottom: var(--spacing-md);
	}
</style>
