import { error, json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { env } from '$env/dynamic/private';
import type { ImageData, GraphCapResponse } from '$lib/api/graphcaps';
import { generateReasoning, getReasoningForImage } from '$lib/api/chain_of_thought';

const GRAPHCAP_ENDPOINT = `${env.API_URL}/agents/generate_reasoning`;

// Generate reasoning
export const POST: RequestHandler = async ({ request }) => {
    console.log("v1/vqa POST");
    try {
        const formData = await request.formData();
        const question = formData.get('question');
        
        if (!question) {
            throw error(400, 'Question is required');
        }

        const response = await fetch(GRAPHCAP_ENDPOINT, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`GraphCap API error: ${response.status}`);
        }
        const data = await response.json() as GraphCapResponse<ImageData>;
        
        return json(data);
    } catch (err) {
        console.error('Error in VQA endpoint:', err);
        throw error(500, {
            message: err instanceof Error ? err.message : 'Internal server error'
        });
    }
};

// Get reasoning for image
export const GET: RequestHandler = async ({ url }) => {
    try {
        const imageId = url.searchParams.get('imageId');
        if (!imageId) {
            throw error(400, 'Image ID is required');
        }

        const reasoning = await getReasoningForImage(imageId);
        return json(reasoning);
    } catch (err) {
        console.error('Error getting reasoning:', err);
        throw error(500, {
            message: err instanceof Error ? err.message : 'Internal server error'
        });
    }
}; 