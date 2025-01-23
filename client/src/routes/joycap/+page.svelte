<script lang="ts">
	import type { Mount } from '$lib/db/schema/mounts';
	import PromptBuilder from './components/PromptBuilder.svelte';

	const { data } = $props<{ data: { mounts: Mount[] } }>();
	const testPath = 'tests/artistic/4.png';
</script>

<div class="flex-coloverflow-auto flex h-full">
	<div class="mx-auto w-1/2">
		<PromptBuilder />
	</div>
	<div class="mx-auto w-1/2">
		<h1 class="mb-4 text-2xl font-bold">JoyCap Configuration</h1>
		<img
			src="/api/v1/test/image?path={testPath}"
			class="max-h-[calc(100vh-14rem)] max-w-full rounded-lg object-contain"
			alt=""
		/>
	</div>
</div>

<style>
	/* Any specific styles can go here */
</style>
