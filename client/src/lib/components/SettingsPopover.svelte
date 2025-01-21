<script lang="ts">
    import { Popover } from "bits-ui";
    import { Button } from "$lib/components/ui/button";
    import { Card } from "$lib/components/ui/card";
    let { name, iconClass, children } = $props();
</script>

<Popover.Root>
  <Popover.Trigger>
    <Button class="h-8">{name}</Button>
    {#if iconClass}
      <i class={iconClass}></i>
    {/if}
  </Popover.Trigger>

  <Popover.Content>
    <Card>
      {@render children()}
    </Card>
  </Popover.Content>
</Popover.Root>

<style>
  /* You can add custom styles here if needed */
</style> 