<script lang="ts">
	import type { DatasetState } from '../dataset.svelte';
	const { datasetState } = $props<{ datasetState: DatasetState }>();
</script>

<div class="space-y-2 p-4">
	<h3 class="mb-4 text-lg font-semibold">Image Details</h3>

	<div class="grid grid-cols-[120px_1fr] gap-2">
		<span class="text-gray-500">File Name:</span>
		<span>{datasetState.selectedImage?.info.relativePath}</span>

		<span class="text-gray-500">Created:</span>
		<span>{new Date(datasetState.selectedImage?.info.createdAt || '').toLocaleString()}</span>

		<span class="text-gray-500">Updated:</span>
		<span>{new Date(datasetState.selectedImage?.info.updatedAt || '').toLocaleString()}</span>

		<span class="text-gray-500">File Size:</span>
		<span
			>{datasetState.selectedImage?.info.fileSize
				? `${(datasetState.selectedImage.info.fileSize / (1024 * 1024)).toFixed(2)} MB`
				: ''}</span
		>

		<span class="text-gray-500">Dimensions:</span>
		<span>{datasetState.selectedImage?.info.width} x {datasetState.selectedImage?.info.height}</span
		>

		<span class="text-gray-500">MIME Type:</span>
		<span>{datasetState.selectedImage?.info.mimeType}</span>

		<span class="text-gray-500">Mount ID:</span>
		<span class="font-mono text-sm">{datasetState.selectedImage?.info.mountId}</span>

		<span class="text-gray-500">Image ID:</span>
		<span class="font-mono text-sm">{datasetState.selectedImage?.info.id}</span>

		<span class="text-gray-500">Hash:</span>
		<span class="break-all font-mono text-sm">{datasetState.selectedImage?.info.hash}</span>
	</div>
</div>
