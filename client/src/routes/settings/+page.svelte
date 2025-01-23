<script lang="ts">
	const { data } = $props();
	import ServerHealth from '$lib/layout/Popovers/ServerHealth.svelte';
	import Settings from '$lib/layout/Popovers/ServerSettings.svelte';

	let inputs = $state({
		workspace: data.workspace,
		api: data.api,
		serverHealth: data.serverHealth
	});

	function updateContexts() {
		// Update contexts logic here
	}
</script>

<div class="container mx-auto space-y-6 p-4">
	<h1 class="text-2xl font-bold">Settings</h1>

	<div class="context-settings">
		<h3>Settings</h3>
		<div class="setting-group">
			<label>
				Workspace Path:
				<input type="text" bind:value={inputs.workspace} />
			</label>
			<label>
				API URL:
				<input type="text" bind:value={inputs.api} />
			</label>
			<button type="button" onclick={updateContexts}>Update Settings</button>
		</div>
	</div>

	<Settings api={inputs.api} workspace={inputs.workspace} />
	{#if data.serverHealth}
		<ServerHealth health={data.serverHealth} />
	{/if}
</div>

<style>
	.context-settings {
		padding: 1rem;
		background: #f5f5f5;
		border-radius: 8px;
		margin-bottom: 2rem;
	}

	.setting-group {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.setting-group label {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	input {
		background-color: #dedede;
		padding: 0.5rem;
		border-radius: 4px;
		border: 1px solid #ccc;
		width: 100%;
		margin: 0.5rem 0;
	}
</style>
