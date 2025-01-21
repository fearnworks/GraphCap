<script lang="ts">
	import { Button } from "$lib/components/ui/button";
	import { toast } from "svelte-sonner";
    import { api } from '$lib/utils/api';
    import type { GraphCapResponse, ImageData } from '$lib/graphcaps';
    import { Card } from "$lib/components/ui/card";
    import { Badge } from "$lib/components/ui/badge";
    import { onDestroy } from 'svelte';

	let selectedFile: File | null = null;
	let caption: GraphCapResponse<ImageData> | null = null;
	let loading = false;
    let previewUrl: string | null = null;

	async function handleFileChange(event: Event) {
		const input = event.target as HTMLInputElement;
		if (input.files && input.files[0]) {
			selectedFile = input.files[0];
            // Create preview URL
            previewUrl = URL.createObjectURL(input.files[0]);
		}
	}

	async function generateCaption() {
		if (!selectedFile) {
			toast.error("Please select an image first");
			return;
		}

		loading = true;
		try {
			const formData = new FormData();
			formData.append("file", selectedFile);

			const response = await api<GraphCapResponse<ImageData>>('/caption', {
                method: 'POST',
                body: formData
            });

			toast.success("Caption generated successfully!");
			caption = response;
		} catch (error) {
			console.error("Error generating caption:", error);
			toast.error("Failed to generate caption");
		} finally {
			loading = false;
		}
	}

    onDestroy(() => {
        if (previewUrl) {
            URL.revokeObjectURL(previewUrl);
        }
    });
</script>

<div class="flex flex-col gap-4 w-full mx-auto p-4">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card class="p-4 md:col-span-1">
            <h3 class="text-lg font-semibold mb-4">Upload Image</h3>
            <input
                type="file"
                accept="image/*"
                on:change={handleFileChange}
                class="file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-primary-foreground hover:file:bg-primary/90 mb-4"
            />
            {#if previewUrl}
                <img src={previewUrl} alt="Preview" class="w-full h-48 object-cover rounded-lg" />
            {/if}
            <Button onclick={generateCaption} disabled={!selectedFile || loading} class="w-full mt-4">
                {#if loading}
                    Generating...
                {:else}
                    Generate Caption
                {/if}
            </Button>
        </Card>

        {#if caption}
            <Card class="p-4 md:col-span-3">
                <h3 class="text-lg font-semibold mb-4">Image Analysis</h3>
                
                <div class="space-y-4">
                    <div>
                        <h4 class="font-medium text-sm text-muted-foreground mb-2">Short Caption</h4>
                        <p class="text-sm">{caption.content.short_caption}</p>
                    </div>

                    <div>
                        <h4 class="font-medium text-sm text-muted-foreground mb-2">Dense Caption</h4>
                        <p class="text-sm">{caption.content.dense_caption}</p>
                    </div>

                    <div>
                        <h4 class="font-medium text-sm text-muted-foreground mb-2">Tags</h4>
                        <div class="flex flex-wrap gap-2">
                            {#each caption.content.tags_list as tag}
                                <Badge 
                                    variant="secondary" 
                                    title="Confidence: {Math.round(tag.confidence * 100)}%"
                                >
                                    {tag.tag}
                                </Badge>
                            {/each}
                        </div>
                    </div>

                    <div>
                        <h4 class="font-medium text-sm text-muted-foreground mb-2">Verification</h4>
                        <p class="text-sm">{caption.content.verification}</p>
                    </div>
                </div>
            </Card>
        {/if}
    </div>
</div> 