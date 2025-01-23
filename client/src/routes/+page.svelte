<!-- FormPage.svelte -->
<script lang="ts">
	import { zod } from 'sveltekit-superforms/adapters';
	import { schema } from './schema.js';
	import { superForm } from 'sveltekit-superforms';
	import SuperDebug from 'sveltekit-superforms';
	import ImageUpload from '$lib/components/ImageUpload.svelte';

	const { data } = $props();
	const superform = superForm(data.form, {
		validators: zod(schema),
		resetForm: true
	});
	const { form, message, enhance } = superform;

	let captionData: {
		tags_list: Array<{
			category: string;
			tag: string;
			confidence: number;
		}>;
		short_caption: string;
		verification: string;
		dense_caption: string;
	} | null = null;

	function handleCaption(event: CustomEvent) {
		captionData = event.detail;
	}
</script>

{#if $message}
	<h4>{$message}</h4>
{/if}

<form method="POST" enctype="multipart/form-data" use:enhance>
	<ImageUpload on:caption={handleCaption} />
</form>

<hr />
Debug
<SuperDebug data={$form} />

<style>
</style>
