<script lang="ts">
	import ImageList  from './ImageList.svelte';
	import { DatasetState } from '$lib/context/dataset.svelte';
	import { Button } from '$lib/components/ui/button';
	import CreateMountForm from './components/CreateMountForm.svelte';
	import MountList from './components/MountList.svelte';
	const { datasetState } = $props<{ datasetState: DatasetState }>();
	let showCreateForm = $state(false);

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

<div class=" space-y-4 rounded-lg bg-slate-700 flex flex-col w-[310px] h-full ">
	<header class="flex items-center justify-between gap-4">
		<div class="flex flex-1 items-center gap-4">
			<div class="w-full h-full flex-col">
				<Button onclick={() => (showCreateForm = !showCreateForm)}>
					{showCreateForm ? 'Cancel' : 'Add Dataset'}
				</Button>
				{#if datasetState.mounts.length}
					<MountList {datasetState} />
				{:else}
					<div class="rounded-lg bg-white p-8 text-center text-gray-500">
						No datasets found. Please add a dataset to continue.
					</div>
				{/if}
			</div>
		</div>
	</header>

	{#if showCreateForm}
		<CreateMountForm />
	{/if}
	<div class="flex-shrink h-full overflow-y-auto">
		{#if datasetState.selectedMount}
			<ImageList {datasetState} />
		{/if}
	</div>
</div>
