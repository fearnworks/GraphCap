<script lang="ts">
	import { fileProxy, filesFieldProxy } from 'sveltekit-superforms';
	const { superform } = $props();
	const { form, errors } = superform;

	const files = filesFieldProxy(superform, 'images');
	const { values, valueErrors } = files;
	const file = fileProxy(form, 'image');
</script>

<div class="container">
	<div class="upload-section">
		<label>
			Upload one file, max 100 MB:
			<input bind:files={$file} accept="image/png, image/jpeg" name="image" type="file" />
			{#if $errors.image}
				<div class="invalid">{$errors.image}</div>
			{/if}
			{#if $file && $file[0]}
				<div class="preview">
					<img src={URL.createObjectURL($file[0])} alt="Single file preview" />
				</div>
			{/if}
		</label>
		<label>
			Upload multiple files, max 100 MB each:
			<input
				multiple
				bind:files={$values}
				accept="image/png, image/jpeg"
				name="images"
				type="file"
			/>
			<ul class="invalid">
				{#each $valueErrors as error, i}
					{#if error}
						<li>Image {i + 1}: {error}</li>
					{/if}
				{/each}
			</ul>
		</label>
	</div>

	<div class="preview-section">
		<h3>Image Previews</h3>
		<div class="preview-grid">
			{#if $values.length > 0}
				{#each $values as file}
					<div class="preview">
						<img src={URL.createObjectURL(file)} alt="Preview" />
					</div>
				{/each}
			{:else}
				<p>No images uploaded yet</p>
			{/if}
		</div>
	</div>
</div>

<style>
	.container {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 2rem;
	}

	.upload-section,
	.preview-section {
		padding: 1rem;
		background: #f5f5f5;
		border-radius: 8px;
	}

	.preview-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
		gap: 1rem;
		margin-top: 1rem;
	}

	.preview {
		margin: 1rem 0;
		max-width: 300px;
	}

	.preview img {
		width: 100%;
		height: auto;
		border-radius: 4px;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	.invalid {
		color: crimson;
		margin: 0.5rem 0;
	}

	label {
		display: block;
		margin-bottom: 1.5rem;
	}

	input {
		width: 100%;
		padding: 0.5rem;
		margin: 0.5rem 0;
		border: 1px solid #ccc;
		border-radius: 4px;
	}
</style>
