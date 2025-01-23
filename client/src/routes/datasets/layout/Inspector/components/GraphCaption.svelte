<script lang="ts">
    import { Button } from '$lib/components/ui/button';
    import { enhance } from '$app/forms';
    import { toast } from 'svelte-sonner';
    import { Card } from '$lib/components/ui/card';
    import TagList from '$lib/components/TagList.svelte';
    
    // Define the DatasetState type inline or create a separate types file
    type DatasetState = {
        selectedImage?: {
            info: {
                id: string;
            };
            captions: Array<{
                shortCaption: string;
                denseCaption: string;
                verification: string;
                tags?: Array<{
                    category: string;
                    tag: string;
                    confidence: number;
                }>;
            }>;
        };
        selectedMount?: {
            id: string;
        };
    };
    
    const { datasetState } = $props<{ datasetState: DatasetState }>();
    
    type CaptionData = {
        tags: Array<{
            category: string;
            tag: string;
            confidence: number;
        }>;
        short_caption: string;
        verification: string;
        dense_caption: string;
    };
    
    let isLoading = $state(false);
    let errorDetails = $state<string | null>(null);

    const existingCaptions = $derived(datasetState.selectedImage?.captions || []);

    async function refreshImageData() {
        fetch(`/api/v1/image?imageId=${datasetState.selectedImage?.info.id}`)
            .then(response => response.json())
            .then(data => {
                console.log(data);
                datasetState.selectedImage = data;
            });
    }

</script>

<div class="space-y-4">
    <div class="flex justify-between items-center">
        <h3 class="text-lg font-semibold">Graph Captions</h3>
        <form
            method="POST"
            action="?/generateCaption"
            use:enhance={() => {
                isLoading = true;
                errorDetails = null;
                return async ({ result }) => {
                    isLoading = false;
                    
                    if (result.type === 'success') {
                        await refreshImageData();
                        toast.success("Caption generated successfully!");
                    } else {
                        console.log(result);
                        const errorMessage = 'data' in result && result.data?.error 
                            ? String(result.data.error)
                            : "Failed to generate caption";
                        errorDetails = errorMessage;
                        toast.error("Failed to generate caption");
                    }
                };
            }}
        >
            <input type="hidden" name="imageId" value={datasetState.selectedImage?.info.id} />
            <input type="hidden" name="mountId" value={datasetState.selectedMount?.id} />
            <Button type="submit" disabled={isLoading || !datasetState.selectedMount?.id}>
                {isLoading ? 'Generating...' : 'Generate New Caption'}
            </Button>
        </form>
    </div>

    {#if errorDetails}
        <div class="p-4 bg-red-50 text-red-700 rounded-lg">
            <p class="font-medium">Error Details:</p>
            <p class="text-sm">{errorDetails}</p>
        </div>
    {/if}

    <div class="space-y-4">
        {#if existingCaptions.length > 0}
            {#each existingCaptions as caption}
                <Card class="p-4">
                    <div class="space-y-4">
                        <div class="flex justify-between items-start">
                            <div>
                                <h4 class="font-medium">Short Caption</h4>
                                <p class="text-sm">{caption.shortCaption}</p>
                            </div>
                            <span class={`px-2 py-1 rounded-full text-xs 
                                ${caption.verification === 'verified' 
                                    ? 'bg-green-100 text-green-800' 
                                    : 'bg-yellow-100 text-yellow-800'}`}>
                                {caption.verification}
                            </span>
                        </div>

                        <div>
                            <h4 class="font-medium">Dense Caption</h4>
                            <p class="text-sm text-muted-foreground">{caption.denseCaption}</p>
                        </div>

                        {#if caption.tags}
                            <div>
                                <h4 class="font-medium mb-2">Tags</h4>
                                <TagList tags={caption.tags} />
                            </div>
                        {/if}
                    </div>
                </Card>
            {/each}
        {:else}
            <div class="text-center p-8 bg-muted rounded-lg">
                <p class="text-muted-foreground">No captions available for this image.</p>
                <p class="text-sm text-muted-foreground mt-1">Generate a new caption to get started.</p>
            </div>
        {/if}
    </div>
</div> 