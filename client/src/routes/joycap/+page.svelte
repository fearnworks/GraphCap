<script lang="ts">
    import type { Mount } from '$lib/db/schema/mounts';
    import PromptBuilder from './components/PromptBuilder.svelte';

    const { data } = $props<{ data : { mounts: Mount[] } }>();
    const testPath = "tests/artistic/4.png"
</script>

<div class="h-full flex flex-coloverflow-auto">
    <div class="w-1/2 mx-auto">
        <PromptBuilder />
    </div>
    <div class="w-1/2 mx-auto">
        <h1 class="text-2xl font-bold mb-4">JoyCap Configuration</h1>
        <img 
            src="/api/v1/test/image?path={testPath}" 
            class="max-w-full max-h-[calc(100vh-14rem)] object-contain rounded-lg"
            alt=""
        />    </div>
</div>

<style>
    /* Any specific styles can go here */
</style>
