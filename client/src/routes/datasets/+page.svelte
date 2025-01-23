<script lang="ts">
	import type { Mount } from '$lib/db/schema/mounts';
	import DatasetExplorer from './layout/DatasetExplorer.svelte';
	import { DatasetState } from './dataset.svelte';

	const { data } = $props<{ data: { mounts: Mount[] } }>();
	let datasetState = $state(new DatasetState());
	datasetState.mounts = data.mounts;
	$inspect(datasetState);
</script>

<div class="h-full overflow-hidden">
	<DatasetExplorer {datasetState} />
</div>

<style>
	/* Any specific styles can go here */
</style>
