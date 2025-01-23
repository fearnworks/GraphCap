import { error, json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { env } from '$env/dynamic/private';
import { saveCaption } from '$lib/db/database';
import type { ImageData, GraphCapResponse } from '$lib/api/graphcaps';
import { createCaption, deleteCaption, getCaptionsForImage, updateCaption } from '$lib/api/caption';

const GRAPHCAP_ENDPOINT = `${env.API_URL}/agents/generate_caption`;

// Generate caption
export const POST: RequestHandler = async ({ request }) => {
	console.log('v1/caption POST');
	try {
		const formData = await request.formData();
		const response = await fetch(GRAPHCAP_ENDPOINT, {
			method: 'POST',
			body: formData
		});

		if (!response.ok) {
			throw new Error(`GraphCap API error: ${response.status}`);
		}
		const data = (await response.json()) as GraphCapResponse<ImageData>;

		return json(data);
	} catch (err) {
		console.error('Error in caption endpoint:', err);
		throw error(500, {
			message: err instanceof Error ? err.message : 'Internal server error'
		});
	}
};

// Get captions for image
export const GET: RequestHandler = async ({ url }) => {
	try {
		const imageId = url.searchParams.get('imageId');
		if (!imageId) {
			throw error(400, 'Image ID is required');
		}

		const captions = await getCaptionsForImage(imageId);
		return json(captions);
	} catch (err) {
		console.error('Error getting captions:', err);
		throw error(500, {
			message: err instanceof Error ? err.message : 'Internal server error'
		});
	}
};

// Update caption
export const PUT: RequestHandler = async ({ request }) => {
	try {
		const { id, ...caption } = await request.json();
		if (!id) {
			throw error(400, 'Caption ID is required');
		}

		const updatedCaption = await updateCaption(id, caption);
		return json(updatedCaption);
	} catch (err) {
		console.error('Error updating caption:', err);
		throw error(500, {
			message: err instanceof Error ? err.message : 'Internal server error'
		});
	}
};

// Delete caption
export const DELETE: RequestHandler = async ({ url }) => {
	try {
		const id = url.searchParams.get('id');
		if (!id) {
			throw error(400, 'Caption ID is required');
		}

		const deletedCaption = await deleteCaption(id);
		return json(deletedCaption);
	} catch (err) {
		console.error('Error deleting caption:', err);
		throw error(500, {
			message: err instanceof Error ? err.message : 'Internal server error'
		});
	}
};
