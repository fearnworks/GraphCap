<script lang="ts">
	import { page } from '$app/stores';
	import { Button } from '$lib/components/ui/button';
	import SettingsPopover from '$lib/components/SettingsPopover.svelte';
	import ServerSettings from '$lib/layout/Popovers/ServerSettings.svelte';
	import type { AppState } from '$lib/context/app-state.svelte';

	export interface FooterProps {
		height: string;
		appState: AppState;
	}
	const { data } = $props<{ data: FooterProps }>();
</script>

<footer class="bg-slate-900 p-1" style:height={data.height}>
	<div class="flex items-center justify-between text-white">
		<div class="h-10 space-x-1">
			<SettingsPopover name="Server" iconClass="fa-solid fa-gear">
				<ServerSettings appState={data.appState} />
			</SettingsPopover>
		</div>
	</div>
</footer>
