<script>
	import { Toaster } from 'svelte-sonner';
	import '../app.css';
	import Navbar from '$lib/layout/NavBar.svelte';
	import Footer from '$lib/layout/Footer.svelte';
	import { AppState } from '$lib/context/app-state.svelte';
	let { data, children } = $props();

	let appState = $state(new AppState());
	console.log(data);
	appState.serverHealth = data.serverHealth;
	appState.serverApi = data.serverApi;
	appState.serverModelInfo = data.serverHealth.modelInfo;
	$inspect(appState);
</script>

<Toaster />
<div class="h-screen w-screen">
	<main class="flex h-full w-full flex-col overflow-hidden bg-slate-600">
		<Navbar height="40px" />
		<div id="main-content" style:height={`calc(100vh - 80px)`}>
			{@render children()}
		</div>
		<Footer data={{ height: '40px', appState }} />
	</main>
</div>
