<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { getProject } from '$lib/api/client';
	import Terminal from '$lib/components/Terminal.svelte';
	import type { Project } from '$lib/types/api';

	let project: Project | null = null;
	let loading = true;
	let error: string | null = null;
	let terminalComponent: Terminal;

	$: projectId = $page.params.id;

	onMount(async () => {
		if (!projectId) {
			error = 'Invalid project ID';
			loading = false;
			return;
		}
		try {
			project = await getProject(projectId);
			if (!project.container_id) {
				error = 'Container not running. Please start the container first.';
			}
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load project';
		} finally {
			loading = false;
		}
	});

	function handleBack() {
		goto(`/projects/${projectId}`);
	}
</script>

<svelte:head>
	<title>Terminal - {project?.name || 'Project'} - Claude Dev Container</title>
</svelte:head>

<div class="terminal-page">
	{#if loading}
		<div class="loading" data-testid="loading">Loading...</div>
	{:else if error}
		<div class="error-container">
			<div class="error card" data-testid="error">
				<h2>Cannot Open Terminal</h2>
				<p>{error}</p>
				<button class="btn-primary" on:click={handleBack}>Back to Project</button>
			</div>
		</div>
	{:else if project && project.container_id}
		<div class="terminal-header">
			<div class="header-info">
				<button class="btn-secondary back-btn" on:click={handleBack} data-testid="back-btn">
					Back
				</button>
				<h1 data-testid="project-name">{project.name}</h1>
			</div>
		</div>
		<div class="terminal-wrapper">
			<Terminal containerId={project.container_id} bind:this={terminalComponent} />
		</div>
	{/if}
</div>

<style>
	.terminal-page {
		display: flex;
		flex-direction: column;
		height: calc(100vh - 80px);
		margin: calc(-1 * var(--spacing-xl));
		padding: var(--spacing-md);
	}

	.terminal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--spacing-md);
		padding: 0 var(--spacing-sm);
	}

	.header-info {
		display: flex;
		align-items: center;
		gap: var(--spacing-md);
	}

	.header-info h1 {
		font-size: 1.25rem;
	}

	.back-btn {
		font-size: 0.875rem;
	}

	.terminal-wrapper {
		flex: 1;
		min-height: 0;
	}

	.loading {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100%;
		color: var(--color-text-muted);
	}

	.error-container {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100%;
	}

	.error {
		text-align: center;
		max-width: 400px;
	}

	.error h2 {
		margin-bottom: var(--spacing-md);
		color: var(--color-error);
	}

	.error p {
		margin-bottom: var(--spacing-lg);
		color: var(--color-text-muted);
	}
</style>
