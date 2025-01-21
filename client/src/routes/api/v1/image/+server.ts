import type { RequestHandler } from "@sveltejs/kit";

import { error, json } from '@sveltejs/kit';
import { getImageWithAnnotations } from '$lib/api/image';

export const GET: RequestHandler = async ({ url }) => {
    try {
        const imageId = url.searchParams.get('imageId');
        if (!imageId) {
            throw error(400, 'Image ID is required');
        }

        const image = await getImageWithAnnotations(imageId);
        return json(image);
    } catch (err) {
        console.error('Error getting image:', err);
        throw error(500, {
            message: err instanceof Error ? err.message : 'Internal server error'
        });
    }
};
