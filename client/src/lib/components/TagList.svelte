<script lang="ts">
    type TagType = 
        | "Entity"
        | "Relationship"
        | "Style"
        | "Attribute"
        | "Composition"
        | "Contextual"
        | "Technical"
        | "Semantic";

    interface Tag {
        category: TagType;
        tag: string;
        confidence: number;
    }

    const { tags } = $props<{ tags: Tag[] }>();

    // Color mapping for different tag types
    const tagColors: Record<TagType, { bg: string; text: string }> = {
        Entity: { bg: 'bg-blue-100', text: 'text-blue-800' },
        Relationship: { bg: 'bg-purple-100', text: 'text-purple-800' },
        Style: { bg: 'bg-pink-100', text: 'text-pink-800' },
        Attribute: { bg: 'bg-green-100', text: 'text-green-800' },
        Composition: { bg: 'bg-yellow-100', text: 'text-yellow-800' },
        Contextual: { bg: 'bg-orange-100', text: 'text-orange-800' },
        Technical: { bg: 'bg-cyan-100', text: 'text-cyan-800' },
        Semantic: { bg: 'bg-indigo-100', text: 'text-indigo-800' }
    };

    function formatConfidence(confidence: number): string {
        return (confidence * 100).toFixed(0) + '%';
    }
</script>

<div class="flex flex-wrap gap-2">
    {#each tags as tag}
        <span 
            class={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                ${tagColors[tag.category as TagType].bg} ${tagColors[tag.category as TagType].text}`}
            title={`Confidence: ${formatConfidence(tag.confidence)}`}
        >
            {tag.tag}
            <span class="ml-1.5 text-xs opacity-75">
                {formatConfidence(tag.confidence)}
            </span>
        </span>
    {/each}
</div>