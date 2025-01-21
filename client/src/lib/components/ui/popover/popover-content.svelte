<script lang="ts">
    import { Popover as PopoverPrimitive } from "bits-ui";
    import { cn } from "$lib/utils";
    import { scale } from "svelte/transition";
    import { quadOut } from "svelte/easing";

    let className: string | undefined = undefined;
    export { className as class };
</script>

<PopoverPrimitive.Content
    transition:scale={{ duration: 200, easing: quadOut }}
    class={cn(
        "z-50 w-72 rounded-md border bg-popover p-4 text-popover-foreground shadow-md outline-none",
        className
    )}
    {...$$restProps}
>
    <slot />
</PopoverPrimitive.Content> 