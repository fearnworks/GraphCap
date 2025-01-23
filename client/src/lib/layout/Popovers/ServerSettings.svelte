<script lang="ts">
	import { getContext } from 'svelte';
	import type { AppState } from '$lib/context/app-state.svelte';
	import ServerHealth from './ServerHealth.svelte';
	let { appState } = $props<{ appState: AppState }>();
</script>

<pre>
    API: {appState.serverApi}
</pre>
<ServerHealth {appState} />
