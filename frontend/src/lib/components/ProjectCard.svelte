<script lang="ts">
	import type { Project } from '$lib/types/api';

	export let project: Project;

	$: containerStatus = project.container_id ? 'running' : 'created';
</script>

<div class="project-card card" data-testid="project-card">
	<div class="card-header">
		<h3 data-testid="project-name">{project.name}</h3>
		<span class="status {containerStatus}" data-testid="project-status">
			{containerStatus}
		</span>
	</div>

	<div class="card-body">
		<p class="path" data-testid="project-path">{project.path}</p>
		<p class="created">
			Created: {new Date(project.created_at).toLocaleDateString()}
		</p>
	</div>

	<div class="card-actions">
		<a href="/projects/{project.id}" class="btn-primary" data-testid="view-project-btn">
			View Project
		</a>
		{#if project.container_id}
			<a
				href="/projects/{project.id}/terminal"
				class="btn-secondary"
				data-testid="open-terminal-btn"
			>
				Open Terminal
			</a>
		{/if}
	</div>
</div>

<style>
	.project-card {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-md);
	}

	.card-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
	}

	.card-header h3 {
		font-size: 1.125rem;
		word-break: break-word;
	}

	.card-body {
		flex: 1;
	}

	.path {
		font-family: 'Monaco', 'Menlo', monospace;
		font-size: 0.875rem;
		color: var(--color-text-muted);
		word-break: break-all;
	}

	.created {
		font-size: 0.75rem;
		color: var(--color-text-muted);
		margin-top: var(--spacing-sm);
	}

	.card-actions {
		display: flex;
		gap: var(--spacing-sm);
		flex-wrap: wrap;
	}

	.card-actions a {
		flex: 1;
		text-align: center;
		padding: var(--spacing-sm) var(--spacing-md);
		border-radius: var(--border-radius);
		font-size: 0.875rem;
		font-weight: 500;
	}

	.card-actions a:hover {
		text-decoration: none;
	}
</style>
