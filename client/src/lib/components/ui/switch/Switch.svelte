<script lang="ts">
    import { Switch, Label } from "bits-ui";
    
    let { 
        checked = $bindable(false),
        labelText = "",
        class: className = "" 
    } = $props();
</script>

<div class={`flex items-center gap-2 ${className}`}>
    <Switch.Root
        bind:checked
        class="inline-flex h-4 w-7 shrink-0 cursor-pointer items-center rounded-full border border-transparent transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-foreground focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:cursor-not-allowed disabled:opacity-50 data-[state=checked]:bg-foreground data-[state=unchecked]:bg-gray-200 dark:data-[state=unchecked]:bg-gray-700"
    >
        <Switch.Thumb
            class="pointer-events-none block h-3 w-3 rounded-full bg-white transition-transform data-[state=checked]:translate-x-3.5 data-[state=unchecked]:translate-x-0.5"
        />
    </Switch.Root>
    <Label.Root class="text-xs cursor-pointer">{labelText}</Label.Root>
</div> 