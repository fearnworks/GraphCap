<script lang="ts">
  import { Button } from '$lib/components/ui/button';
  import { Menubar } from 'bits-ui';
  import { ChevronRight } from 'lucide-svelte';
  
  // For TypeScript, define props interface
  interface $$Props {
      height?: string;
  }
  
  let { height} = $props();
  
  // Navigation state using Svelte 5 runes
  let currentView = $state('home');
</script>

<nav class="bg-slate-900 border-b" style:height={height}>
  <Menubar.Root class="flex items-center px-4">
      <Button size="sm">
        <a href="/">Home</a>
      </Button>
      <Button size="sm">  
        <a href="/datasets">Datasets</a>  
      </Button>
      <Button size="sm">  
        <a href="/debug">Debug</a>  
      </Button>
      <div class="ml-auto bg-slate-800 text-white">
      <Menubar.Menu >
          <Menubar.Trigger class="bg-slate-800 text-white">

              Test Menu
          </Menubar.Trigger>
          <Menubar.Content
              class="z-50 min-w-[200px] rounded-md border bg-slate-800 p-1 shadow-md"
              sideOffset={5}
          >
              <Menubar.Item
                  class="relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-slate-700 focus:bg-slate-700"
              >
                  <a href="/" class="flex w-full items-center">Home</a>
              </Menubar.Item>
              
              <Menubar.Item
                  class="relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-slate-700 focus:bg-slate-700"
              >
                  <a href="/datasets" class="flex w-full items-center">Datasets</a>
              </Menubar.Item>

              <Menubar.Separator class="my-1 h-px bg-muted" />

              <Menubar.Sub>
                  <Menubar.SubTrigger
                      class="relative flex w-full cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-slate-700 focus:bg-slate-700"
                  >
                      Tools
                      <div class="ml-auto">
                          <ChevronRight class="h-4 w-4" />
                      </div>
                  </Menubar.SubTrigger>
                  <Menubar.SubContent
                      class="z-50 min-w-[180px] rounded-md border bg-slate-800 p-1 shadow-md"
                  >
                      <Menubar.Item
                          class="relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-slate-700 focus:bg-slate-700"
                      >
                          <a href="/joycap" class="flex w-full items-center">Joycap</a>
                      </Menubar.Item>
                      <Menubar.Item
                          class="relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors "
                      >
                          <a href="/debug" class="flex w-full items-center">Debug</a>
                      </Menubar.Item>
                  </Menubar.SubContent>
              </Menubar.Sub>
          </Menubar.Content>
      </Menubar.Menu>

      <div class="ml-auto flex items-center space-x-4">

      </div>
  </Menubar.Root>
</nav> 