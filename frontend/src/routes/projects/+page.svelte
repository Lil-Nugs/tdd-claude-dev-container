<script lang="ts">
	import { onMount } from 'svelte';
	import { getProjects, createProject } from '$lib/api/client';
	import ProjectCard from '$lib/components/ProjectCard.svelte';
	import type { Project, CreateProject } from '$lib/types/api';

	let projects: Project[] = [];
	let loading = true;
	let error: string | null = null;

	// Create project form
	let showCreateForm = false;
	let newProject: CreateProject = { name: '', path: '' };
	let creating = false;
	let createError: string | null = null;

	onMount(async () => {
		await loadProjects();
	});

	async function loadProjects() {
		loading = true;
		error = null;
		try {
			projects = await getProjects();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load projects';
		} finally {
			loading = false;
		}
	}

	async function handleCreateProject() {
		if (!newProject.name || !newProject.path) {
			createError = 'Name and path are required';
			return;
		}

		creating = true;
		createError = null;

		try {
			const project = await createProject(newProject);
			projects = [project, ...projects];
			newProject = { name: '', path: '' };
			showCreateForm = false;
		} catch (e) {
			createError = e instanceof Error ? e.message : 'Failed to create project';
		} finally {
			creating = false;
		}
	}

	function cancelCreate() {
		showCreateForm = false;
		newProject = { name: '', path: '' };
		createError = null;
	}
</script>

<svelte:head>
	<title>Projects - Claude Dev Container</title>
</svelte:head>

<div class="projects-page">
	<div class="page-header">
		<h1>Projects</h1>
		<button
			class="btn-primary"
			on:click={() => (showCreateForm = !showCreateForm)}
			data-testid="create-project-btn"
		>
			{showCreateForm ? 'Cancel' : 'New Project'}
		</button>
	</div>

	{#if showCreateForm}
		<div class="create-form card" data-testid="create-project-form">
			<h2>Create New Project</h2>
			<form on:submit|preventDefault={handleCreateProject}>
				<div class="form-group">
					<label for="project-name">Project Name</label>
					<input
						id="project-name"
						type="text"
						bind:value={newProject.name}
						placeholder="My Project"
						data-testid="project-name-input"
					/>
				</div>
				<div class="form-group">
					<label for="project-path">Project Path</label>
					<input
						id="project-path"
						type="text"
						bind:value={newProject.path}
						placeholder="/path/to/project"
						data-testid="project-path-input"
					/>
				</div>
				{#if createError}
					<div class="form-error" data-testid="create-error">{createError}</div>
				{/if}
				<div class="form-actions">
					<button type="button" class="btn-secondary" on:click={cancelCreate}>Cancel</button>
					<button type="submit" class="btn-primary" disabled={creating} data-testid="submit-btn">
						{creating ? 'Creating...' : 'Create Project'}
					</button>
				</div>
			</form>
		</div>
	{/if}

	<div class="projects-content">
		{#if loading}
			<div class="loading" data-testid="loading">Loading projects...</div>
		{:else if error}
			<div class="error" data-testid="error">
				<p>{error}</p>
				<button class="btn-secondary" on:click={loadProjects}>Retry</button>
			</div>
		{:else if projects.length === 0}
			<div class="empty" data-testid="empty">
				<h2>No projects yet</h2>
				<p>Create your first project to get started with Claude Dev Container.</p>
				<button class="btn-primary" on:click={() => (showCreateForm = true)}>
					Create Your First Project
				</button>
			</div>
		{:else}
			<div class="projects-grid" data-testid="projects-grid">
				{#each projects as project (project.id)}
					<ProjectCard {project} />
				{/each}
			</div>
		{/if}
	</div>
</div>

<style>
	.projects-page {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-xl);
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.page-header h1 {
		font-size: 2rem;
	}

	.create-form {
		max-width: 500px;
	}

	.create-form h2 {
		margin-bottom: var(--spacing-lg);
	}

	.form-group {
		margin-bottom: var(--spacing-md);
	}

	.form-group label {
		display: block;
		font-size: 0.875rem;
		font-weight: 500;
		margin-bottom: var(--spacing-xs);
		color: var(--color-text-muted);
	}

	.form-group input {
		width: 100%;
		padding: var(--spacing-sm) var(--spacing-md);
		font-size: 1rem;
		background-color: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--border-radius);
		color: var(--color-text);
	}

	.form-group input:focus {
		outline: none;
		border-color: var(--color-primary);
	}

	.form-error {
		color: var(--color-error);
		font-size: 0.875rem;
		margin-bottom: var(--spacing-md);
	}

	.form-actions {
		display: flex;
		gap: var(--spacing-sm);
		justify-content: flex-end;
	}

	.projects-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
		gap: var(--spacing-lg);
	}

	.loading,
	.error,
	.empty {
		text-align: center;
		padding: var(--spacing-xl);
	}

	.error {
		color: var(--color-error);
	}

	.error p {
		margin-bottom: var(--spacing-md);
	}

	.empty {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--spacing-md);
		color: var(--color-text-muted);
	}

	.empty h2 {
		color: var(--color-text);
	}
</style>
