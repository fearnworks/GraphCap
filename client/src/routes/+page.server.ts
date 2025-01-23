import type { Actions, PageServerLoad } from './$types.js';
import { superValidate, message, withFiles } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { fail } from '@sveltejs/kit';
import { schema } from './schema.js';
import { API_URL, WORKSPACE } from '$lib/constants';

export const load: PageServerLoad = async () => {
	// Fetch initial server health
	let serverHealth = { status: 'unknown', modelInfo: null, error: null };

	try {
		const [healthResponse, modelInfoResponse] = await Promise.all([
			fetch(`${API_URL}/server/health`),
			fetch(`${API_URL}/server/model_info`)
		]);

		if (healthResponse.ok && modelInfoResponse.ok) {
			const health = await healthResponse.json();
			const modelInfo = await modelInfoResponse.json();
			serverHealth = {
				status: health.status,
				modelInfo,
				error: null
			};
		}
	} catch (error) {
		console.error('Error fetching server health:', error);
	}

	return {
		form: await superValidate(zod(schema)),
		api: API_URL,
		workspace: WORKSPACE,
		serverHealth
	};
};

export const actions: Actions = {
	default: async ({ request }) => {
		const form = await superValidate(request, zod(schema));
		console.dir(form, { depth: 8 });

		if (!form.valid) return fail(400, withFiles({ form }));

		// Process the uploaded files
		const formData = form.data;

		return message(form, 'Files uploaded successfully!');
	}
};
