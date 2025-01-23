<script lang="ts">
	import { DropdownMenu } from 'bits-ui';
	import type { Mount } from '$lib/db/schema/mounts';
	import { Button } from '$lib/components/ui/button';
	import { Check, ChevronDown } from 'lucide-svelte';
	import { DatasetState } from '$lib/context/dataset.svelte';

	const { datasetState } = $props<{ datasetState: DatasetState }>();

	let selectedMountId = $state<string | null>(null);

	async function handleSelect(mount: Mount) {
		selectedMountId = mount.id;
		datasetState.selectedMount = mount;
		let mountFiles = await fetch(`/api/v1/mounts/${selectedMountId}/files`);
		datasetState.mountFiles = await mountFiles.json();
	}

	const selectedMount = $derived(
		selectedMountId
			? datasetState.mounts.find((mount: Mount) => mount.id === selectedMountId)
			: null
	);
</script>

<div class="">
	<DropdownMenu.Root>
		<DropdownMenu.Trigger class="w-full">
			<Button variant="outline" class="w-full justify-between">
				<span>
					{selectedMount?.name ?? 'Select Dataset'}
				</span>
				<ChevronDown class="h-4 w-4 opacity-50" />
			</Button>
		</DropdownMenu.Trigger>

		<DropdownMenu.Content class="w-[250px] bg-slate-100 p-2">
			{#each datasetState.mounts as mount}
				<DropdownMenu.Item
					class="flex cursor-pointer items-center justify-between rounded-md px-3 py-2 hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
					onclick={() => handleSelect(mount)}
				>
					<div class="flex flex-col gap-0.5">
						<span class="font-medium">{mount.name}</span>
						{#if mount.description}
							<span class="text-sm text-muted-foreground">{mount.description}</span>
						{/if}
						<span class="text-xs text-muted-foreground opacity-80">{mount.path}</span>
					</div>
					{#if selectedMountId === mount.id}
						<Check class="ml-2 h-4 w-4 flex-shrink-0" />
					{/if}
				</DropdownMenu.Item>
			{/each}
		</DropdownMenu.Content>
	</DropdownMenu.Root>
</div>
