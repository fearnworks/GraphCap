import { db } from '$lib/db';
import { imageInfo, annotations, captionAnnotations, chainOfThoughtAnnotations } from '$lib/db/schema';
import { eq } from 'drizzle-orm';
import type { ImageInfo } from '$lib/db/schema/image-info';
import type { CaptionAnnotation } from '$lib/db/schema/caption-annotations';
import type { ChainOfThoughtAnnotation } from '$lib/db/schema/chain-of-thought-annotations';

// Aggregated type for an image with all its annotations
export interface AggregatedImage {
    info: ImageInfo;
    captions: CaptionAnnotation[];
    chainOfThoughts: ChainOfThoughtAnnotation[];
}

// Get all annotations for an image
export async function getImageWithAnnotations(imageId: string): Promise<AggregatedImage | null> {
    // Get base image info
    const [baseImage] = await db
        .select()
        .from(imageInfo)
        .where(eq(imageInfo.id, imageId));

    if (!baseImage) {
        return null;
    }

    // Get all annotations for this image
    const [captions, chainOfThoughts] = await Promise.all([
        // Get captions
        db
            .select({
                id: captionAnnotations.id,
                shortCaption: captionAnnotations.shortCaption,
                verification: captionAnnotations.verification,
                denseCaption: captionAnnotations.denseCaption,
                tags: captionAnnotations.tags
            })
            .from(captionAnnotations)
            .innerJoin(annotations, eq(annotations.id, captionAnnotations.annotationId))
            .where(eq(annotations.imageId, imageId)),

        // Get chain of thoughts
        db
            .select({
                id: chainOfThoughtAnnotations.id,
                problemAnalysis: chainOfThoughtAnnotations.problemAnalysis,
                contextAnalysis: chainOfThoughtAnnotations.contextAnalysis,
                solutionOutline: chainOfThoughtAnnotations.solutionOutline,
                solutionPlan: chainOfThoughtAnnotations.solutionPlan,
                response: chainOfThoughtAnnotations.response,
                question: chainOfThoughtAnnotations.question
            })
            .from(chainOfThoughtAnnotations)
            .innerJoin(annotations, eq(annotations.id, chainOfThoughtAnnotations.annotationId))
            .where(eq(annotations.imageId, imageId))
    ]);

    return {
        info: baseImage,
        captions,
        chainOfThoughts
    };
}

// Get multiple images with their annotations
export async function getImagesWithAnnotations(imageIds: string[]): Promise<AggregatedImage[]> {
    const results = await Promise.all(
        imageIds.map(id => getImageWithAnnotations(id))
    );
    
    // Filter out null results
    return results.filter((result): result is AggregatedImage => result !== null);
}

// Get latest images with annotations (with optional limit)
export async function getLatestImagesWithAnnotations(limit: number = 10): Promise<AggregatedImage[]> {
    const latestImages = await db
        .select()
        .from(imageInfo)
        .orderBy(imageInfo.createdAt)
        .limit(limit);

    return getImagesWithAnnotations(latestImages.map(img => img.id));
}

// Get images by mount with annotations
export async function getImagesByMountWithAnnotations(mountId: string): Promise<AggregatedImage[]> {
    const mountImages = await db
        .select()
        .from(imageInfo)
        .where(eq(imageInfo.mountId, mountId));

    return getImagesWithAnnotations(mountImages.map(img => img.id));
}

export async function getAllImagesWithAnnotations() {
    const images = await db.select().from(imageInfo);
    return getImagesWithAnnotations(images.map(img => img.id));
}