<script lang="ts">
	import { onMount } from 'svelte';
	import { getProjects } from '$lib/api/client';
	import ProjectCard from '$lib/components/ProjectCard.svelte';
	import type { Project } from '$lib/types/api';

	let projects: Project[] = [];
	let loading = true;
	let error: string | null = null;

	onMount(async () => {
		try {
			projects = await getProjects();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load projects';
		} finally {
			loading = false;
		}
	});
</script>

<svelte:head>
	<title>Dashboard - Claude Dev Container</title>
</svelte:head>

<div class="dashboard">
	<section class="hero">
		<h1>Claude Dev Container</h1>
		<p>AI-powered development environment for your projects</p>
	</section>

	<section class="overview">
		<div class="stats">
			<div class="stat-card card">
				<h3>Projects</h3>
				<p class="stat-value" data-testid="project-count">{projects.length}</p>
			</div>
			<div class="stat-card card">
				<h3>Active Containers</h3>
				<p class="stat-value" data-testid="active-containers">
					{projects.filter(p => p.container_id).length}
				</p>
			</div>
		</div>
	</section>

	<section class="recent-projects">
		<div class="section-header">
			<h2>Recent Projects</h2>
			<a href="/projects" class="btn-secondary">View All</a>
		</div>

		{#if loading}
			<div class="loading" data-testid="loading">Loading projects...</div>
		{:else if error}
			<div class="error" data-testid="error">{error}</div>
		{:else if projects.length === 0}
			<div class="empty" data-testid="empty">
				<p>No projects yet. Create your first project to get started.</p>
				<a href="/projects" class="btn-primary">Create Project</a>
			</div>
		{:else}
			<div class="projects-grid" data-testid="projects-grid">
				{#each projects.slice(0, 4) as project (project.id)}
					<ProjectCard {project} />
				{/each}
			</div>
		{/if}
	</section>
</div>

<style>
	.dashboard {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-xl);
	}

	.hero {
		text-align: center;
		padding: var(--spacing-xl) 0;
	}

	.hero h1 {
		font-size: 2.5rem;
		margin-bottom: var(--spacing-sm);
	}

	.hero p {
		color: var(--color-text-muted);
		font-size: 1.125rem;
	}

	.stats {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: var(--spacing-lg);
	}

	.stat-card {
		text-align: center;
	}

	.stat-card h3 {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		text-transform: uppercase;
		margin-bottom: var(--spacing-sm);
	}

	.stat-value {
		font-size: 2.5rem;
		font-weight: 700;
		color: var(--color-primary);
	}

	.section-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--spacing-lg);
	}

	.section-header h2 {
		font-size: 1.5rem;
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
		color: var(--color-text-muted);
	}

	.error {
		color: var(--color-error);
	}

	.empty {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--spacing-md);
	}
</style>
