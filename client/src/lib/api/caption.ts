import { API_URL } from '$lib/constants';
import { error } from '@sveltejs/kit';
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { db } from '$lib/db';
import { imageInfo, mounts, annotations, captionAnnotations } from '$lib/db/schema';
import { eq, and, isNull } from 'drizzle-orm';
import type { NewCaptionAnnotation, ImageTag } from '$lib/db/schema/caption-annotations';

type CaptionRequest = {
	imageId: string;
	mountId: string;
};

export async function getCaptionsForImage(imageId: string) {
	return await db
		.select({
			id: captionAnnotations.id,
			shortCaption: captionAnnotations.shortCaption,
			verification: captionAnnotations.verification,
			denseCaption: captionAnnotations.denseCaption,
			tags: captionAnnotations.tags
		})
		.from(captionAnnotations)
		.innerJoin(annotations, eq(annotations.id, captionAnnotations.annotationId))
		.where(eq(annotations.imageId, imageId));
}

export async function createCaption(caption: NewCaptionAnnotation) {
	const [newCaption] = await db.insert(captionAnnotations).values(caption).returning();
	return newCaption;
}

export async function updateCaption(id: string, caption: Partial<NewCaptionAnnotation>) {
	const [updatedCaption] = await db
		.update(captionAnnotations)
		.set(caption)
		.where(eq(captionAnnotations.id, id))
		.returning();
	return updatedCaption;
}

export async function deleteCaption(id: string) {
	const [deletedCaption] = await db
		.delete(captionAnnotations)
		.where(eq(captionAnnotations.id, id))
		.returning();
	return deletedCaption;
}

export const generateCaption = async ({ imageId, mountId }: CaptionRequest) => {
	try {
		console.log('Starting caption generation for:', { mountId, imageId });

		const [mount] = await db.select().from(mounts).where(eq(mounts.id, mountId));

		if (!mount) {
			console.error('Mount not found:', mountId);
			throw error(404, 'Mount not found');
		}

		const [image] = await db.select().from(imageInfo).where(eq(imageInfo.id, imageId));

		if (!image) {
			console.error('Image not found:', imageId);
			throw error(404, 'Image not found');
		}

		const fullPath = join(mount.path, image.relativePath);
		console.log('Full path:', fullPath);

		if (!existsSync(fullPath)) {
			console.error('File not found:', fullPath);
			throw error(404, 'File not found');
		}

		const fileBuffer = readFileSync(fullPath);
		const fileFormData = new FormData();
		const fileName = image.relativePath.split('/').pop();
		fileFormData.append('file', new Blob([fileBuffer]), fileName);

		console.log('Sending request to API:', `${API_URL}/agents/generate_caption`);
		console.log('With file:', fileName);

		const response = await fetch(`${API_URL}/agents/generate_caption`, {
			method: 'POST',
			body: fileFormData
		});

		console.log('API Response status:', response.status);
		const responseText = await response.text();
		console.log('API Response body:', responseText);

		if (!response.ok) {
			throw error(response.status, `Failed to generate caption: ${responseText}`);
		}

		const captionData = JSON.parse(responseText);
		console.log('Caption data:', captionData);

		// Create an annotation first
		const [newAnnotation] = await db
			.insert(annotations)
			.values({
				imageId,
				type: 'caption',
				createdAt: new Date(),
				updatedAt: new Date()
			})
			.returning();

		// Create the caption annotation with tags
		const [newCaption] = await db
			.insert(captionAnnotations)
			.values({
				annotationId: newAnnotation.id,
				shortCaption: captionData.content.short_caption || 'No short caption provided',
				verification: 'unverified',
				denseCaption: captionData.content.dense_caption || 'No dense caption provided',
				tags: captionData.content.tags_list || []
			})
			.returning();

		return {
			success: true,
			caption: captionData.content,
			savedCaption: newCaption
		};
	} catch (err: unknown) {
		console.error('Caption generation error:', err);
		const errorMessage = err instanceof Error ? err.message : 'Failed to generate caption';
		return { success: false, error: errorMessage };
	}
};

export const getAllCaptions = async () => {
	console.log('Getting all captions');
	return await db
		.select({
			id: captionAnnotations.id,
			shortCaption: captionAnnotations.shortCaption,
			verification: captionAnnotations.verification,
			denseCaption: captionAnnotations.denseCaption,
			tags: captionAnnotations.tags
		})
		.from(captionAnnotations);
};

export async function queueCaptionsForMount(mountId: string) {
	try {
		// Get all images for this mount that don't have captions
		const uncaptionedImages = await db
			.select({
				id: imageInfo.id,
				relativePath: imageInfo.relativePath
			})
			.from(imageInfo)
			.leftJoin(
				annotations,
				and(eq(annotations.imageId, imageInfo.id), eq(annotations.type, 'caption'))
			)
			.where(and(eq(imageInfo.mountId, mountId), isNull(annotations.id)));

		console.log(`Found ${uncaptionedImages.length} uncaptioned images`);

		// Queue each image for captioning
		const results = await Promise.allSettled(
			uncaptionedImages.map((img) => generateCaption({ imageId: img.id, mountId }))
		);

		// Analyze results
		const successful = results.filter((r) => r.status === 'fulfilled' && r.value.success).length;
		const failed = results.filter(
			(r) => r.status === 'rejected' || (r.status === 'fulfilled' && !r.value.success)
		).length;

		return {
			success: true,
			results: {
				total: uncaptionedImages.length,
				successful,
				failed,
				completionRate: `${((successful / uncaptionedImages.length) * 100).toFixed(1)}%`
			}
		};
	} catch (error) {
		console.error('Error queuing captions:', error);
		const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
		return { success: false, error: errorMessage };
	}
}
