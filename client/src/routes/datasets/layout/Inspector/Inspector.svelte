<script lang="ts">
    import GraphCaption from './components/GraphCaption.svelte';
    import VQAReasoner from './components/VQAReasoner.svelte';
    import ImageDetails from './components/ImageDetails.svelte';
    import type { DatasetState } from '../../dataset.svelte';
    import { Tabs, TabsContent, TabsList, TabsTrigger } from '$lib/components/ui/tabs';
    const { datasetState } = $props<{ datasetState: DatasetState }>();
    let formElement: HTMLFormElement;
    $inspect(datasetState);
    $effect(() => {
        if (formElement) {
            const formData = new FormData(formElement);
            const submitEvent = new SubmitEvent('submit', { cancelable: true });
            formElement.dispatchEvent(submitEvent);
        }
    });
</script>

<div class="border rounded-lg bg-white overflow-auto min-w-[40%] max-w-[40%]">
    {#if datasetState.selectedImage}
        <Tabs value="image-details">
            <TabsList class="w-full mb-4">
                <TabsTrigger value="image-details" class="flex-1">Details</TabsTrigger>
                <TabsTrigger value="graph-caption" class="flex-1">Graph Caption</TabsTrigger>
                <TabsTrigger value="vqa-reasoner" class="flex-1">VQA Reasoner</TabsTrigger>
            </TabsList>
            <TabsContent value="graph-caption">
                <GraphCaption datasetState={datasetState} />
            </TabsContent>
            <TabsContent value="image-details">
                <ImageDetails datasetState={datasetState} />
            </TabsContent>
            <TabsContent value="vqa-reasoner">
                <VQAReasoner datasetState={datasetState} />
            </TabsContent>
        </Tabs>
    {:else}
        <div class="p-4 text-center text-gray-500">
            Select an image to view details
        </div>
    {/if}
</div>