<script lang="ts">
	import {
		Table,
		TableBody,
		TableCell,
		TableHead,
		TableHeader,
		TableRow
	} from '$lib/components/ui/table';
	import type { CaptionAnnotation } from '$lib/db/schema/caption-annotations';

	let { data } = $props();

	const formatDate = (date: string) => {
		return new Date(date).toLocaleDateString();
	};
</script>

<div class="container mx-auto py-10">
	<h1 class="mb-6 text-2xl font-bold">Caption Overview</h1>

	<Table>
		<TableHeader>
			<TableRow>
				<TableHead>ID</TableHead>
				<TableHead>Short Caption</TableHead>
				<TableHead>Dense Caption</TableHead>
				<TableHead>Verification Status</TableHead>
			</TableRow>
		</TableHeader>
		<TableBody>
			{#each data.captions as caption}
				<TableRow>
					<TableCell class="font-mono text-sm">{caption.id}</TableCell>
					<TableCell>{caption.shortCaption}</TableCell>
					<TableCell class="max-w-md">
						<div class="truncate">
							{caption.denseCaption}
						</div>
					</TableCell>
					<TableCell>
						<span
							class={`rounded-full px-2 py-1 text-xs ${
								caption.verification === 'verified'
									? 'bg-green-100 text-green-800'
									: 'bg-yellow-100 text-yellow-800'
							}`}
						>
							{caption.verification}
						</span>
					</TableCell>
				</TableRow>
			{/each}
		</TableBody>
	</Table>
</div>
