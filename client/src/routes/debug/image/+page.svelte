<script lang="ts">
	import {
		Table,
		TableBody,
		TableCell,
		TableHead,
		TableHeader,
		TableRow
	} from '$lib/components/ui/table';
	import { ChevronDown, ChevronRight } from 'lucide-svelte';

	let { data } = $props();

	let expandedRows = $state(new Set<string>());

	function toggleRow(imageId: string) {
		if (expandedRows.has(imageId)) {
			expandedRows.delete(imageId);
		} else {
			expandedRows.add(imageId);
		}
	}

	function formatFileSize(bytes: number) {
		const units = ['B', 'KB', 'MB', 'GB'];
		let size = bytes;
		let unitIndex = 0;
		while (size >= 1024 && unitIndex < units.length - 1) {
			size /= 1024;
			unitIndex++;
		}
		return `${size.toFixed(1)} ${units[unitIndex]}`;
	}

	function formatDate(date: string) {
		return new Date(date).toLocaleString();
	}
</script>

<div class="container mx-auto max-h-[80vh] overflow-y-auto py-10">
	<h1 class="mb-6 text-2xl font-bold">Image Overview</h1>

	<Table>
		<TableHeader>
			<TableRow>
				<TableHead class="w-8"></TableHead>
				<TableHead>Path</TableHead>
				<TableHead>Size</TableHead>
				<TableHead>Dimensions</TableHead>
				<TableHead>Type</TableHead>
				<TableHead>Created</TableHead>
				<TableHead>Annotations</TableHead>
			</TableRow>
		</TableHeader>
		<TableBody>
			{#each data.images as image}
				<TableRow class="cursor-pointer" onclick={() => toggleRow(image.info.id)}>
					<TableCell>
						{#if expandedRows.has(image.info.id)}
							<ChevronDown class="h-4 w-4" />
						{:else}
							<ChevronRight class="h-4 w-4" />
						{/if}
					</TableCell>
					<TableCell class="font-medium">{image.info.relativePath}</TableCell>
					<TableCell>{formatFileSize(image.info.fileSize)}</TableCell>
					<TableCell>{image.info.width} × {image.info.height}</TableCell>
					<TableCell>{image.info.mimeType}</TableCell>
					<TableCell>{formatDate(image.info.createdAt.toISOString())}</TableCell>
					<TableCell>
						<div class="flex gap-2">
							{#if image.captions.length > 0}
								<span class="rounded-full bg-blue-100 px-2 py-1 text-xs text-blue-800">
									{image.captions.length} Captions
								</span>
							{/if}
							{#if image.chainOfThoughts.length > 0}
								<span class="rounded-full bg-purple-100 px-2 py-1 text-xs text-purple-800">
									{image.chainOfThoughts.length} CoT
								</span>
							{/if}
						</div>
					</TableCell>
				</TableRow>
				{#if expandedRows.has(image.info.id)}
					<TableRow>
						<TableCell colspan="7" class="bg-muted/50">
							<div class="p-4">
								{#if image.captions.length > 0}
									<div class="mb-4">
										<h3 class="mb-2 font-semibold">Captions</h3>
										{#each image.captions as caption}
											<div class="mb-2 rounded-lg bg-white p-3 shadow-sm">
												<p class="font-medium">{caption.shortCaption}</p>
												<p class="mt-1 text-sm text-muted-foreground">{caption.denseCaption}</p>
												<span
													class={`mt-2 inline-block rounded-full px-2 py-1 text-xs ${
														caption.verification === 'verified'
															? 'bg-green-100 text-green-800'
															: 'bg-yellow-100 text-yellow-800'
													}`}>
													{caption.verification}
												</span>
											</div>
										{/each}
									</div>
								{/if}

								{#if image.chainOfThoughts.length > 0}
									<div>
										<h3 class="mb-2 font-semibold">Chain of Thoughts</h3>
										{#each image.chainOfThoughts as cot}
											<div class="mb-2 rounded-lg bg-white p-3 shadow-sm">
												<div class="grid grid-cols-2 gap-4">
													<div>
														<h4 class="font-medium">Problem Analysis</h4>
														<p class="text-sm">{cot.problemAnalysis}</p>
													</div>
													<div>
														<h4 class="font-medium">Context Analysis</h4>
														<p class="text-sm">{cot.contextAnalysis}</p>
													</div>
												</div>
												<div class="mt-3">
													<h4 class="font-medium">Solution</h4>
													<p class="text-sm">{cot.solutionOutline}</p>
												</div>
											</div>
										{/each}
									</div>
								{/if}
							</div>
						</TableCell>
					</TableRow>
				{/if}
			{/each}
		</TableBody>
	</Table>
</div>
