<!-- FormPage.svelte -->
<script lang="ts">
    import { zod } from 'sveltekit-superforms/adapters';
    import { schema } from './schema.js';
    import { superForm } from 'sveltekit-superforms';
    import SuperDebug from 'sveltekit-superforms';
    import FileUpload from './FileUpload.svelte';
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
    .context-settings {
        padding: 1rem;
        background: #f5f5f5;
        border-radius: 8px;
        margin-bottom: 2rem;
    }

    .setting-group {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .setting-group label {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    input {
        background-color: #dedede;
        padding: 0.5rem;
        border-radius: 4px;
        border: 1px solid #ccc;
        width: 100%;
        margin: 0.5rem 0;
    }
</style>
  