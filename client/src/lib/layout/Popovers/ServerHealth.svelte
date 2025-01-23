<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { invalidateAll } from '$app/navigation';
	import type { AppState } from '$lib/context/app-state.svelte';

	let { appState } = $props<{ appState: AppState }>();

	let healthCheckInterval: NodeJS.Timeout;
	console.log('Health Init');
	console.log(appState.serverHealth);
	console.log(appState.serverHealth.status);
	onMount(() => {
		// Invalidate data every 30 seconds to trigger a server-side health check
		healthCheckInterval = setInterval(() => {
			invalidateAll();
		}, 30000);
	});

	onDestroy(() => {
		if (healthCheckInterval) {
			clearInterval(healthCheckInterval);
		}
	});
</script>

<div class="server-health {appState.serverHealth.status}">
	<h3>Server Status</h3>
	<div class="status-indicator">
		<span class="dot"></span>
		<span class="status-text">
			{appState.serverHealth.status === 'healthy'
				? 'Online'
				: appState.serverHealth.status === 'error'
					? 'Offline'
					: 'Unknown'}
		</span>
	</div>

	{#if appState.serverHealth.error}
		<div class="error-message">
			{appState.serverHealth.error}
		</div>
	{/if}

	{#if appState.serverHealth.modelInfo && appState.serverHealth.status === 'healthy'}
		<div class="model-info">
			<h4>Model Information</h4>
			<ul>
				<li>Model: {appState.serverHealth.modelInfo.model_name}</li>
				<li>Class: {appState.serverHealth.modelInfo.model_class}</li>
				{#if appState.serverHealth.modelInfo.cuda_device_name}
					<li>GPU: {appState.serverHealth.modelInfo.cuda_device_name}</li>
					<li>GPU Count: {appState.serverHealth.modelInfo.cuda_device_count}</li>
				{/if}
			</ul>
		</div>
	{/if}
</div>

<style>
	.server-health {
		padding: 1rem;
		border-radius: 8px;
		margin-bottom: 1rem;
		background: #f5f5f5;
	}

	.status-indicator {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin: 0.5rem 0;
	}

	.dot {
		width: 12px;
		height: 12px;
		border-radius: 50%;
		display: inline-block;
	}

	.healthy .dot {
		background-color: #4caf50;
	}

	.error .dot {
		background-color: #f44336;
	}

	.unknown .dot {
		background-color: #ffc107;
	}

	.error-message {
		color: #f44336;
		margin-top: 0.5rem;
	}

	.model-info {
		margin-top: 1rem;
		padding-top: 1rem;
		border-top: 1px solid #ddd;
	}

	.model-info h4 {
		margin: 0 0 0.5rem 0;
	}

	.model-info ul {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.model-info li {
		margin: 0.25rem 0;
	}
</style>
