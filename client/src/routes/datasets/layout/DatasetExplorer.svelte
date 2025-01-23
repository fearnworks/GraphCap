<script lang="ts">
	import { DatasetState } from '$lib/context/dataset.svelte';
	import Inspector from './Inspector/Inspector.svelte';
	import Viewport from './Viewport/Viewport.svelte';
	import DatasetSidebar from './Sidebar/DatasetSidebar.svelte';
	const { datasetState } = $props<{ datasetState: DatasetState }>();
	let formElement: HTMLFormElement;
	$inspect(datasetState);
	$effect(() => {
		if (formElement) {
			const formData = new FormData(formElement);
			const submitEvent = new SubmitEvent('submit', { cancelable: true });
			formElement.dispatchEvent(submitEvent);
		}
	});
</script>

<div class="flex h-full w-full flex-row space-y-4 overflow-hidden">
	<!-- File Browser -->
	<DatasetSidebar {datasetState} />

	{#if datasetState.selectedMount}
		<!-- Image Preview -->
		<Viewport {datasetState} />

		<!-- Image Details Sidebar -->
		<Inspector {datasetState} />
	{:else}
		<div class="rounded-lg bg-white p-8 text-center text-gray-500">
			Select a dataset to view its contents
		</div>
	{/if}
</div>
