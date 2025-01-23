<script lang="ts">
	import { DatasetState } from '$lib/context/dataset.svelte';
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

<!-- Image Preview -->
<div class="flex flex-grow flex-col items-center justify-center rounded-lg border bg-white p-4">
	{#if datasetState.selectedImage}
		<img
			src="/api/v1/mounts/{datasetState.selectedMount.id}/image?path={datasetState.selectedImage
				.info.relativePath}"
			class="max-h-[calc(100vh-14rem)] max-w-full rounded-lg object-contain"
			alt=""
		/>
	{:else}
		<div class="text-center text-gray-500">Select an image to preview</div>
	{/if}
</div>
