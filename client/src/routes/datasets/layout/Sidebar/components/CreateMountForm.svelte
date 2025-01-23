<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { enhance } from '$app/forms';

	let formData = $state({
		name: '',
		path: '',
		description: ''
	});
</script>

<form
	method="POST"
	action="?/createMount"
	use:enhance
	class="space-y-4 rounded-lg border bg-white p-4"
>
	<div class="space-y-2">
		<Label for="name">Name</Label>
		<Input
			id="name"
			name="name"
			bind:value={formData.name}
			placeholder="e.g., Training Images"
			required
		/>
	</div>

	<div class="space-y-2">
		<Label for="path">Path</Label>
		<Input
			id="path"
			name="path"
			bind:value={formData.path}
			placeholder="/path/to/dataset"
			required
		/>
	</div>

	<div class="space-y-2">
		<Label for="description">Description</Label>
		<Input
			id="description"
			name="description"
			bind:value={formData.description}
			placeholder="Optional description"
		/>
	</div>

	<Button type="submit" class="w-full">Create Mount</Button>
</form>
