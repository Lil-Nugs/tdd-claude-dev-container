<script lang="ts">
	import '../app.css';
</script>

<div class="app">
	<header>
		<nav>
			<a href="/" class="logo">Claude Dev Container</a>
			<ul>
				<li><a href="/">Dashboard</a></li>
				<li><a href="/projects">Projects</a></li>
			</ul>
		</nav>
	</header>

	<main>
		<slot />
	</main>
</div>

<style>
	.app {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
	}

	header {
		background-color: var(--color-bg-secondary);
		border-bottom: 1px solid var(--color-border);
		padding: var(--spacing-md) var(--spacing-xl);
	}

	nav {
		display: flex;
		align-items: center;
		justify-content: space-between;
		max-width: 1400px;
		margin: 0 auto;
	}

	.logo {
		font-size: 1.25rem;
		font-weight: 700;
		color: var(--color-text);
	}

	.logo:hover {
		color: var(--color-primary);
		text-decoration: none;
	}

	ul {
		display: flex;
		list-style: none;
		gap: var(--spacing-lg);
	}

	li a {
		color: var(--color-text-muted);
		font-weight: 500;
	}

	li a:hover {
		color: var(--color-primary);
		text-decoration: none;
	}

	main {
		flex: 1;
		padding: var(--spacing-xl);
		max-width: 1400px;
		margin: 0 auto;
		width: 100%;
	}
</style>
