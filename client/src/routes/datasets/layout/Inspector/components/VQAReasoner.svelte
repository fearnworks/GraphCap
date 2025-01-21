<script lang="ts">
    import { Button } from '$lib/components/ui/button';
    import { Input } from '$lib/components/ui/input';
    import type { DatasetState } from '$lib/context/dataset.svelte';
    import { enhance } from '$app/forms';
    import { toast } from 'svelte-sonner';
    import { Card } from '$lib/components/ui/card';
    import { Accordion } from 'bits-ui';
    import { ChevronDown } from 'lucide-svelte';
    
    const { datasetState } = $props<{ datasetState: DatasetState }>();
    
    let isLoading = $state(false);
    let errorDetails = $state<string | null>(null);
    let question = $state('');

    const existingReasoning = $derived(datasetState.selectedImage?.chainOfThoughts || []);

    async function refreshImageData() {
        fetch(`/api/v1/image?imageId=${datasetState.selectedImage?.info.id}`)
            .then(response => response.json())
            .then(data => {
                datasetState.selectedImage = data;
            });
    }
</script>

<style>
    .formatted-text {
        white-space: pre-wrap;
        word-wrap: break-word;
        line-height: 1.5;
    }

    .accordion-content {
        padding: 0.5rem 0;
    }

    .section-title {
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--muted-foreground);
        margin-bottom: 0.25rem;
    }
</style>

<div class="space-y-4">
    <div class="flex justify-between items-center">
        <h3 class="text-lg font-semibold">Visual Question Answering</h3>
    </div>

    <form
        method="POST"
        action="?/generateReasoning"
        use:enhance={() => {
            isLoading = true;
            errorDetails = null;
            return async ({ result }) => {
                isLoading = false;
                if (result.type === 'success' && 'data' in result && result.data?.reasoning) {
                    await refreshImageData();
                    toast.success("Reasoning generated successfully!");
                    question = '';
                } else {
                    const errorMessage = 'data' in result && result.data?.error 
                        ? String(result.data.error)
                        : "Failed to generate reasoning";
                    errorDetails = errorMessage;
                    toast.error("Failed to generate reasoning");
                }
            };
        }}
        class="space-y-4"
    >
        <input type="hidden" name="imageId" value={datasetState.selectedImage?.info.id} />
        <input type="hidden" name="mountId" value={datasetState.selectedMount?.id} />
        
        <div class="flex gap-4">
            <Input
                type="text"
                name="question"
                bind:value={question}
                placeholder="Ask a question about the image..."
                class="flex-1"
            />
            <Button 
                type="submit" 
                disabled={isLoading || !datasetState.selectedMount?.id || !question.trim()}
            >
                {isLoading ? 'Analyzing...' : 'Ask Question'}
            </Button>
        </div>
    </form>

    {#if errorDetails}
        <div class="p-4 bg-red-50 text-red-700 rounded-lg">
            <p class="font-medium">Error Details:</p>
            <p class="text-sm">{errorDetails}</p>
        </div>
    {/if}

    <div class="space-y-4">
        {#if existingReasoning.length > 0}
            {#each existingReasoning as reasoning}
                <Card class="p-4">
                    <Accordion.Root 
                        type="multiple" 
                        value={['question', 'response']} 
                        class="w-full"
                    >
                        <Accordion.Item value="question" class="border-b border-dark-10">
                            <Accordion.Header>
                                <Accordion.Trigger class="flex w-full justify-between py-2">
                                    <span class="font-medium">Question</span>
                                    <ChevronDown class="h-4 w-4 transition-transform duration-200" />
                                </Accordion.Trigger>
                            </Accordion.Header>
                            <Accordion.Content class="accordion-content">
                                <p class="formatted-text text-sm text-muted-foreground">{reasoning.question}</p>
                            </Accordion.Content>
                        </Accordion.Item>

                        <Accordion.Item value="analysis" class="border-b border-dark-10">
                            <Accordion.Header>
                                <Accordion.Trigger class="flex w-full justify-between py-2">
                                    <span class="font-medium">Analysis</span>
                                    <ChevronDown class="h-4 w-4 transition-transform duration-200" />
                                </Accordion.Trigger>
                            </Accordion.Header>
                            <Accordion.Content class="accordion-content">
                                <div class="grid grid-cols-2 gap-4">
                                    <div>
                                        <h4 class="section-title">Problem Analysis</h4>
                                        <p class="formatted-text text-sm text-muted-foreground">{reasoning.problemAnalysis}</p>
                                    </div>
                                    <div>
                                        <h4 class="section-title">Context Analysis</h4>
                                        <p class="formatted-text text-sm text-muted-foreground">{reasoning.contextAnalysis}</p>
                                    </div>
                                </div>
                            </Accordion.Content>
                        </Accordion.Item>

                        <Accordion.Item value="solution" class="border-b border-dark-10">
                            <Accordion.Header>
                                <Accordion.Trigger class="flex w-full justify-between py-2">
                                    <span class="font-medium">Solution</span>
                                    <ChevronDown class="h-4 w-4 transition-transform duration-200" />
                                </Accordion.Trigger>
                            </Accordion.Header>
                            <Accordion.Content class="accordion-content">
                                <div class="space-y-3">
                                    <div>
                                        <h4 class="section-title">Solution Outline</h4>
                                        <p class="formatted-text text-sm text-muted-foreground">{reasoning.solutionOutline}</p>
                                    </div>
                                    <div>
                                        <h4 class="section-title">Solution Plan</h4>
                                        <p class="formatted-text text-sm text-muted-foreground">{reasoning.solutionPlan}</p>
                                    </div>
                                </div>
                            </Accordion.Content>
                        </Accordion.Item>

                        <Accordion.Item value="response" class="border-b border-dark-10">
                            <Accordion.Header>
                                <Accordion.Trigger class="flex w-full justify-between py-2">
                                    <span class="font-medium">Final Response</span>
                                    <ChevronDown class="h-4 w-4 transition-transform duration-200" />
                                </Accordion.Trigger>
                            </Accordion.Header>
                            <Accordion.Content class="accordion-content">
                                <p class="formatted-text text-sm">{reasoning.response}</p>
                            </Accordion.Content>
                        </Accordion.Item>
                    </Accordion.Root>
                </Card>
            {/each}
        {:else}
            <div class="text-center p-8 bg-muted rounded-lg">
                <p class="text-muted-foreground">No questions have been asked about this image.</p>
                <p class="text-sm text-muted-foreground mt-1">Ask a question to get started.</p>
            </div>
        {/if}
    </div>
</div> 