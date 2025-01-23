export enum CaptionMode {
	DESCRIPTIVE = 'descriptive',
	TRAINING = 'training',
	MIDJOURNEY = 'midjourney',
	BOORU_TAGS = 'booru_tags',
	BOORU_LIKE_TAGS = 'booru_like_tags',
	ART_CRITIC = 'art_critic',
	PRODUCT_LISTING = 'product_listing',
	SOCIAL_MEDIA = 'social_media'
}

export enum ToneStyle {
	FORMAL = 'formal',
	CASUAL = 'casual',
	TECHNICAL = 'technical',
	CREATIVE = 'creative',
	PROFESSIONAL = 'professional'
}

export interface PromptOptions {
	exclude_unchangeable_attributes: boolean;
	include_lighting: boolean;
	include_camera_angle: boolean;
	include_watermark_info: boolean;
	include_artifact_info: boolean;
	include_camera_details: boolean;
	keep_pg: boolean;
	exclude_resolution: boolean;
	include_quality_assessment: boolean;
	include_composition: boolean;
	exclude_text: boolean;
	include_depth_of_field: boolean;
	include_lighting_source: boolean;
	avoid_ambiguity: boolean;
	include_sfw_rating: boolean;
	only_important_elements: boolean;
}

export interface PromptConfig {
	config_name: string;
	mode: CaptionMode;
	tone: ToneStyle;
	use_case?: string;
	description?: string;
	word_count?: number;
	length?: string;
	options: PromptOptions;
}

export const defaultOptions: PromptOptions = {
	exclude_unchangeable_attributes: false,
	include_lighting: false,
	include_camera_angle: false,
	include_watermark_info: false,
	include_artifact_info: false,
	include_camera_details: false,
	keep_pg: false,
	exclude_resolution: true,
	include_quality_assessment: false,
	include_composition: false,
	exclude_text: true,
	include_depth_of_field: false,
	include_lighting_source: false,
	avoid_ambiguity: true,
	include_sfw_rating: false,
	only_important_elements: true
};

export const presetConfigs: PromptConfig[] = [
	{
		config_name: 'descriptive_formal',
		mode: CaptionMode.DESCRIPTIVE,
		tone: ToneStyle.FORMAL,
		use_case: 'Content Description',
		description:
			'Formal description focusing on key elements of the image. Ideal for accessibility, content indexing, and general documentation.',
		options: { ...defaultOptions }
	},
	{
		config_name: 'art_critic',
		mode: CaptionMode.ART_CRITIC,
		tone: ToneStyle.FORMAL,
		use_case: 'Art Analysis',
		description:
			'Detailed artistic analysis including composition, lighting, and quality assessment.',
		options: {
			...defaultOptions,
			include_composition: true,
			include_lighting: true,
			include_quality_assessment: true
		}
	},
	{
		config_name: 'technical_photo',
		mode: CaptionMode.TRAINING,
		tone: ToneStyle.TECHNICAL,
		use_case: 'Photography Technical Analysis',
		description:
			'Technical analysis of photographic elements including camera settings, lighting, and composition.',
		options: {
			...defaultOptions,
			include_camera_details: true,
			include_lighting: true,
			include_depth_of_field: true,
			include_composition: true
		}
	},
	{
		config_name: 'artistic_technical',
		mode: CaptionMode.TRAINING,
		tone: ToneStyle.TECHNICAL,
		use_case: 'Photography Technical Analysis',
		description:
			'Technical analysis of photographic elements including camera settings, lighting, and composition.',
		options: {
			...defaultOptions,
			include_camera_details: true,
			include_lighting: true,
			include_depth_of_field: true,
			include_composition: true
		}
	}
];

export function buildBasePrompt(config: PromptConfig): string {
	let base = '';
	switch (config.mode) {
		case CaptionMode.DESCRIPTIVE:
			base = `Write a descriptive caption for this image in a ${config.tone} tone`;
			break;
		case CaptionMode.TRAINING:
			base = 'Write a stable diffusion prompt for this image';
			break;
		case CaptionMode.MIDJOURNEY:
			base = 'Write a MidJourney prompt for this image';
			break;
		case CaptionMode.BOORU_TAGS:
			base = 'Write a list of Booru tags for this image';
			break;
		case CaptionMode.BOORU_LIKE_TAGS:
			base = 'Write a list of Booru-like tags for this image';
			break;
		case CaptionMode.ART_CRITIC:
			base =
				'Analyze this image like an art critic would with information about its composition, style, symbolism, the use of color, light, any artistic movement it might belong to, etc';
			break;
		case CaptionMode.PRODUCT_LISTING:
			base = 'Write a caption for this image as though it were a product listing';
			break;
		case CaptionMode.SOCIAL_MEDIA:
			base = 'Write a caption for this image as if it were being used for a social media post';
			break;
	}

	if (config.word_count) {
		base += ` within ${config.word_count} words`;
	} else if (config.length) {
		base += `. Keep it ${config.length}`;
	}

	return base;
}

export function buildExtraInstructions(options: PromptOptions): string[] {
	const instructions: string[] = [];

	if (options.exclude_unchangeable_attributes) {
		instructions.push(
			'Do NOT include information about people/characters that cannot be changed (like ethnicity, gender, etc), but do still include changeable attributes (like hair style)'
		);
	}
	if (options.include_lighting) {
		instructions.push('Include information about lighting');
	}
	if (options.include_camera_angle) {
		instructions.push('Include information about camera angle');
	}
	if (options.include_watermark_info) {
		instructions.push('Include information about whether there is a watermark or not');
	}
	if (options.include_artifact_info) {
		instructions.push('Include information about whether there are JPEG artifacts or not');
	}
	if (options.include_camera_details) {
		instructions.push(
			'If it is a photo you MUST include information about what camera was likely used and details such as aperture, shutter speed, ISO, etc'
		);
	}
	if (options.keep_pg) {
		instructions.push('Do NOT include anything sexual; keep it PG');
	}
	if (options.exclude_resolution) {
		instructions.push("Do NOT mention the image's resolution");
	}
	if (options.include_quality_assessment) {
		instructions.push(
			'You MUST include information about the subjective aesthetic quality of the image from low to very high'
		);
	}
	if (options.include_composition) {
		instructions.push(
			"Include information on the image's composition style, such as leading lines, rule of thirds, or symmetry"
		);
	}
	if (options.exclude_text) {
		instructions.push('Do NOT mention any text that is in the image');
	}
	if (options.include_depth_of_field) {
		instructions.push(
			'Specify the depth of field and whether the background is in focus or blurred'
		);
	}
	if (options.include_lighting_source) {
		instructions.push(
			'If applicable, mention the likely use of artificial or natural lighting sources'
		);
	}
	if (options.avoid_ambiguity) {
		instructions.push('Do NOT use any ambiguous language');
	}
	if (options.include_sfw_rating) {
		instructions.push('Include whether the image is sfw, suggestive, or nsfw');
	}
	if (options.only_important_elements) {
		instructions.push('ONLY describe the most important elements of the image');
	}

	return instructions;
}

export function buildPrompt(config: PromptConfig): string {
	const base = buildBasePrompt(config);
	const instructions = buildExtraInstructions(config.options);

	return [base, ...instructions].join('. ') + '.';
}
