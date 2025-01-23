<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import { Card } from '$lib/components/ui/card';
	import { Label } from 'bits-ui';
	import CustomSwitch from '$lib/components/ui/switch/Switch.svelte';
	import { Textarea } from '$lib/components/ui/textarea';
	import { DropdownMenu } from 'bits-ui';
	import { ChevronDown } from 'lucide-svelte';
	import {
		type PromptConfig,
		type PromptOptions,
		CaptionMode,
		ToneStyle,
		defaultOptions,
		presetConfigs,
		buildPrompt
	} from './prompt_builder';

	let config = $state<PromptConfig>({
		config_name: 'custom',
		mode: CaptionMode.DESCRIPTIVE,
		tone: ToneStyle.FORMAL,
		options: { ...defaultOptions }
	});

	const modes = Object.entries(CaptionMode).map(([label, value]) => ({
		label,
		value
	}));

	const tones = Object.entries(ToneStyle).map(([label, value]) => ({
		label,
		value
	}));

	let generatedPrompt = $derived(buildPrompt(config));

	function handleOptionChange(key: keyof PromptOptions, checked: boolean) {
		config.options[key] = checked;
	}

	function handleModeChange(values: string[]) {
		config.mode = values[0] as CaptionMode;
	}

	function handleToneChange(values: string[]) {
		config.tone = values[0] as ToneStyle;
	}

	function loadPresetConfig(presetName: string) {
		const preset = presetConfigs.find((p) => p.config_name === presetName);
		if (preset) {
			config = { ...preset };
		}
	}

	const optionCategories = {
		general: [
			{ key: 'exclude_unchangeable_attributes', label: 'Exclude Unchangeable Attributes' },
			{ key: 'keep_pg', label: 'Keep PG' },
			{ key: 'exclude_resolution', label: 'Exclude Resolution' },
			{ key: 'avoid_ambiguity', label: 'Avoid Ambiguity' },
			{ key: 'only_important_elements', label: 'Only Important Elements' }
		],
		imageDetails: [
			{ key: 'include_lighting', label: 'Include Lighting' },
			{ key: 'include_camera_angle', label: 'Include Camera Angle' },
			{ key: 'include_watermark_info', label: 'Include Watermark Info' },
			{ key: 'include_artifact_info', label: 'Include Artifact Info' },
			{ key: 'include_camera_details', label: 'Include Camera Details' },
			{ key: 'include_depth_of_field', label: 'Include Depth of Field' },
			{ key: 'include_lighting_source', label: 'Include Lighting Source' }
		],
		qualityAssessment: [
			{ key: 'include_quality_assessment', label: 'Include Quality Assessment' },
			{ key: 'include_composition', label: 'Include Composition' },
			{ key: 'include_sfw_rating', label: 'Include SFW Rating' }
		],
		textOptions: [{ key: 'exclude_text', label: 'Exclude Text' }]
	} as const;
</script>

<div class="mx-auto flex h-full max-w-6xl flex-col gap-3 p-3">
	<div class="grid grid-cols-1 gap-3 md:grid-cols-2">
		<!-- Config Section -->
		<Card class="p-3">
			<h2 class="mb-3 text-base font-semibold">Prompt Configuration</h2>

			<!-- Preset Configuration -->
			<div class="mb-3 space-y-1.5">
				<Label.Root class="text-xs font-medium">Preset Configuration</Label.Root>
				<DropdownMenu.Root>
					<DropdownMenu.Trigger class="w-full">
						<Button variant="outline" class="w-full justify-between">
							<span class="truncate">{config.config_name ?? 'Select Preset'}</span>
							<ChevronDown class="ml-2 h-4 w-4 shrink-0 opacity-50" />
						</Button>
					</DropdownMenu.Trigger>
					<DropdownMenu.Content class="w-[200px] rounded-md border bg-background shadow-md">
						{#each presetConfigs as preset}
							<DropdownMenu.Item
								class="cursor-pointer px-2 py-1.5 hover:bg-accent hover:text-accent-foreground"
								onclick={() => loadPresetConfig(preset.config_name)}
							>
								<div class="flex flex-col">
									<span class="font-medium">{preset.config_name}</span>
									{#if preset.description}
										<span class="text-xs text-muted-foreground">{preset.description}</span>
									{/if}
								</div>
							</DropdownMenu.Item>
						{/each}
					</DropdownMenu.Content>
				</DropdownMenu.Root>
			</div>

			<!-- Mode and Tone Selectors -->
			<div class="grid grid-cols-2 gap-3">
				<div class="space-y-1.5">
					<Label.Root class="text-xs font-medium">Mode</Label.Root>
					<DropdownMenu.Root>
						<DropdownMenu.Trigger class="w-full">
							<Button variant="outline" class="w-full justify-between">
								<span>
									{modes.find((mode) => mode.value === config.mode)?.label ?? 'Select Mode'}
								</span>
								<ChevronDown class="h-4 w-4 opacity-50" />
							</Button>
						</DropdownMenu.Trigger>
						<DropdownMenu.Content class="w-[200px] bg-slate-100 p-1">
							{#each modes as mode}
								<DropdownMenu.Item
									class="flex cursor-pointer items-center justify-between rounded-md px-2 py-1 hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
									onclick={() => handleModeChange([mode.value])}
								>
									<span class="font-medium">{mode.label}</span>
								</DropdownMenu.Item>
							{/each}
						</DropdownMenu.Content>
					</DropdownMenu.Root>
				</div>
				<div class="space-y-1.5">
					<Label.Root class="text-xs font-medium">Tone</Label.Root>
					<DropdownMenu.Root>
						<DropdownMenu.Trigger class="w-full">
							<Button variant="outline" class="w-full justify-between">
								<span>
									{tones.find((tone) => tone.value === config.tone)?.label ?? 'Select Tone'}
								</span>
								<ChevronDown class="h-4 w-4 opacity-50" />
							</Button>
						</DropdownMenu.Trigger>
						<DropdownMenu.Content class="w-[200px] bg-slate-100 p-1">
							{#each tones as tone}
								<DropdownMenu.Item
									class="flex cursor-pointer items-center justify-between rounded-md px-2 py-1 hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
									onclick={() => handleToneChange([tone.value])}
								>
									<span class="font-medium">{tone.label}</span>
								</DropdownMenu.Item>
							{/each}
						</DropdownMenu.Content>
					</DropdownMenu.Root>
				</div>
			</div>
		</Card>

		<!-- Preview Section -->
		<Card class="p-3">
			<h2 class="mb-3 text-base font-semibold">Generated Prompt</h2>
			<Textarea
				value={generatedPrompt}
				readonly
				class="min-h-[180px] resize-none bg-muted/50 text-sm"
				rows={7}
			/>
		</Card>
	</div>

	<!-- Options Grid - Merged text options and quality assessment -->
	<div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
		<!-- General Options -->
		<Card class="p-3">
			<h3 class="mb-2 text-xs font-semibold uppercase text-muted-foreground">general</h3>
			<div class="space-y-1.5">
				{#each optionCategories.general as { key, label }}
					<CustomSwitch
						checked={config.options[key]}
						onCheckedChange={(checked) => handleOptionChange(key, checked)}
						labelText={label}
						class="flex items-center space-x-2 text-xs"
					/>
				{/each}
			</div>
		</Card>

		<!-- Image Details -->
		<Card class="p-3">
			<h3 class="mb-2 text-xs font-semibold uppercase text-muted-foreground">image details</h3>
			<div class="space-y-1.5">
				{#each optionCategories.imageDetails as { key, label }}
					<CustomSwitch
						checked={config.options[key]}
						onCheckedChange={(checked) => handleOptionChange(key, checked)}
						labelText={label}
						class="flex items-center space-x-2 text-xs"
					/>
				{/each}
			</div>
		</Card>

		<!-- Combined Quality & Text Options -->
		<Card class="p-3">
			<h3 class="mb-2 text-xs font-semibold uppercase text-muted-foreground">
				quality & text options
			</h3>
			<div class="space-y-1.5">
				{#each [...optionCategories.qualityAssessment, ...optionCategories.textOptions] as { key, label }}
					<CustomSwitch
						checked={config.options[key]}
						onCheckedChange={(checked) => handleOptionChange(key, checked)}
						labelText={label}
						class="flex items-center space-x-2 text-xs"
					/>
				{/each}
			</div>
		</Card>
	</div>

	<!-- Action Buttons -->
	<div class="mt-2 flex justify-end gap-2">
		<Button
			variant="outline"
			size="sm"
			onclick={() => {
				config = {
					config_name: 'custom',
					mode: CaptionMode.DESCRIPTIVE,
					tone: ToneStyle.FORMAL,
					options: { ...defaultOptions }
				};
			}}
		>
			Reset
		</Button>
		<Button size="sm">Save Configuration</Button>
	</div>
</div>
