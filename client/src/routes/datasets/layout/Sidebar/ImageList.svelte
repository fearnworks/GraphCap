<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import { Tabs, TabsContent, TabsList, TabsTrigger } from '$lib/components/ui/tabs';
	import { enhance } from '$app/forms';
	import { DatasetState } from '$lib/context/dataset.svelte';
	import type { FileSystemItem } from '$lib/mounts/mount-manager';
	import { toast } from 'svelte-sonner';
	const { datasetState } = $props<{ datasetState: DatasetState }>();
	let mount = datasetState.selectedMount;
	let currentPath = $state('');
	let isIndexing = $state(false);
	let indexingResults = $state<any>(null);
	let formElement: HTMLFormElement;
	let isQueueingCaptions = $state(false);
	let queueResults = $state<any>(null);
	$inspect(datasetState);
	$effect(() => {
		if (formElement) {
			const formData = new FormData(formElement);
			const submitEvent = new SubmitEvent('submit', { cancelable: true });
			formElement.dispatchEvent(submitEvent);
		}
	});

	function isImageFile(filename: string) {
		return /\.(jpg|jpeg|png|gif|webp)$/i.test(filename);
	}

	function getParentPath(path: string) {
		return path.split('/').slice(0, -1).join('/');
	}

	async function refreshFiles() {
		if (formElement) {
			const formData = new FormData(formElement);
			const submitEvent = new SubmitEvent('submit', { cancelable: true });
			formElement.dispatchEvent(submitEvent);
		}
	}

	function handleSelectImage(file: FileSystemItem) {
		console.log(file);
		fetch(`/api/v1/image?imageId=${file.imageId}`)
			.then((response) => response.json())
			.then((data) => {
				console.log(data);
				datasetState.selectedImage = data;
			});
	}

	async function handleQueueCaptions() {
		if (!mount?.id) return;

		const form = new FormData();
		form.append('mountId', mount.id);

		try {
			isQueueingCaptions = true;
			const response = await fetch('?/queueCaptions', {
				method: 'POST',
				body: form
			});
			const result = await response.json();

			if (result.type === 'success') {
				queueResults = result.data.results;
				toast.success(
					`Successfully queued captions: ${result.data.results.successful}/${result.data.results.total} images`
				);
			} else {
				toast.error(`Failed to queue captions: ${result.error}`);
			}
		} catch (error) {
			toast.error('Failed to queue captions');
		} finally {
			isQueueingCaptions = false;
		}
	}
</script>

<div class="space-y-4">
	<!-- <div class="grid grid-cols-[250px_minmax(0,1fr)_40%] gap-4"> -->
	<div class="flex">
		<!-- File Browser -->

		<div class="rounded-lg border bg-white p-4">
			<div class="mb-4 flex items-center justify-between">
				<Button
					variant="outline"
					size="sm"
					onclick={handleQueueCaptions}
					disabled={isQueueingCaptions || !mount?.id}
				>
					{isQueueingCaptions ? 'Queuing...' : 'Queue All Captions'}
				</Button>
			</div>

			{#if queueResults}
				<div class="mb-4 rounded bg-gray-50 p-2 text-sm">
					<div>Queued: {queueResults.successful}/{queueResults.total}</div>
					<div>Failed: {queueResults.failed}</div>
					<div>Completion Rate: {queueResults.completionRate}</div>
				</div>
			{/if}

			<form
				bind:this={formElement}
				method="POST"
				action="?/listFiles"
				use:enhance={() => {
					return async ({ result }) => {
						if (result.type === 'success' && result.data) {
							datasetState.mountFiles = result.data;
						} else {
							console.error('Failed to load files:', result);
						}
					};
				}}
			>
				<input type="hidden" name="mountId" value={mount.id} />
				<input type="hidden" name="path" value={currentPath} />

				<Tabs value="indexed" class="w-full ">
					<TabsList class="mb-4 w-full">
						<TabsTrigger value="indexed" class="flex">
							Indexed ({datasetState.mountFiles?.stats.indexed})
						</TabsTrigger>
						<TabsTrigger value="unindexed" class="flex">
							Unindexed ({datasetState.mountFiles?.stats.unindexed})
						</TabsTrigger>
					</TabsList>

					<div class="space-y-1">
						<TabsContent value="indexed">
							<div class="mb-1 text-sm font-medium text-gray-500">Files</div>
							{#each datasetState.mountFiles?.indexedFiles as file}
								{#if isImageFile(file.name)}
									<div class="flex items-center justify-between">
										<Button
											variant="ghost"
											class="justify-start"
											onclick={() => handleSelectImage(file)}
										>
											🖼️ {file.name}
										</Button>
									</div>
								{/if}
							{/each}
						</TabsContent>

						<TabsContent value="unindexed">
							<div class="space-y-4">
								<div class="flex items-center justify-between">
									<div class="text-sm font-medium text-gray-500">Files</div>
									<form
										method="POST"
										action="?/indexFiles"
										use:enhance={() => {
											isIndexing = true;
											indexingResults = null;

											return async ({ result }) => {
												isIndexing = false;
												if (result.type === 'success') {
													indexingResults = result.data?.results;
													await refreshFiles();
												} else {
													console.error('Indexing failed:', result);
												}
											};
										}}
									>
										<input type="hidden" name="mountId" value={mount.id} />
										<input type="hidden" name="path" value={currentPath} />
										<Button
											type="submit"
											variant="outline"
											size="sm"
											disabled={isIndexing || datasetState.mountFiles?.unindexedFiles.length === 0}
										>
											{#if isIndexing}
												Indexing...
											{:else}
												Index All ({datasetState.mountFiles?.unindexedFiles.length})
											{/if}
										</Button>
									</form>
								</div>
							</div></TabsContent
						>
					</div>
				</Tabs>
			</form>
		</div>
	</div>
</div>
