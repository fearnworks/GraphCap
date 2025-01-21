import { API_URL } from '$lib/constants';
import { error } from '@sveltejs/kit';
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { db } from '$lib/db';
import { imageInfo, mounts, annotations, chainOfThoughtAnnotations } from '$lib/db/schema';
import { eq, and, isNull } from 'drizzle-orm';
import type { NewChainOfThoughtAnnotation } from '$lib/db/schema/chain-of-thought-annotations';

type ReasoningRequest = {
    imageId: string;
    mountId: string;
    question: string;
}

export async function getReasoningForImage(imageId: string) {
    return await db
        .select()
        .from(chainOfThoughtAnnotations)
        .innerJoin(annotations, eq(annotations.id, chainOfThoughtAnnotations.annotationId))
        .where(eq(annotations.imageId, imageId));
}

export const generateReasoning = async ({ imageId, mountId, question }: ReasoningRequest) => {
    try {
        console.log('Starting reasoning generation for:', { mountId, imageId, question });
        
        // Fetch mount and validate
        const [mount] = await db
            .select()
            .from(mounts)
            .where(eq(mounts.id, mountId));

        if (!mount) {
            console.error('Mount not found:', mountId);
            throw error(404, 'Mount not found');
        }

        // Fetch image and validate
        const [image] = await db
            .select()
            .from(imageInfo)
            .where(eq(imageInfo.id, imageId));

        if (!image) {
            console.error('Image not found:', imageId);
            throw error(404, 'Image not found');
        }

        // Prepare file
        const fullPath = join(mount.path, image.relativePath);
        console.log('Full path:', fullPath);
        
        if (!existsSync(fullPath)) {
            console.error('File not found:', fullPath);
            throw error(404, 'File not found');
        }

        // Create form data with file and question
        const fileBuffer = readFileSync(fullPath);
        const formData = new FormData();
        const fileName = image.relativePath.split('/').pop();
        formData.append('file', new Blob([fileBuffer]), fileName);
        formData.append('question', question);
        
        console.log('Sending request to API:', `${API_URL}/agents/generate_reasoning`);
        
        // Make API request
        const response = await fetch(`${API_URL}/agents/generate_reasoning`, {
            method: 'POST',
            body: formData
        });

        console.log('API Response status:', response.status);
        const responseText = await response.text();
        console.log('API Response body:', responseText);

        if (!response.ok) {
            throw error(response.status, `Failed to generate reasoning: ${responseText}`);
        }

        const reasoningData = JSON.parse(responseText);
        console.log('Reasoning data:', reasoningData);

        // Create annotation
        const [newAnnotation] = await db
            .insert(annotations)
            .values({
                imageId,
                type: 'chain_of_thought',
                createdAt: new Date(),
                updatedAt: new Date()
            })
            .returning();
        console.log('question', question);
        // Create chain of thought annotation with question
        const [newReasoning] = await db
            .insert(chainOfThoughtAnnotations)
            .values({
                annotationId: newAnnotation.id,
                question: question,
                problemAnalysis: reasoningData.content.scratchpad.problem_analysis,
                contextAnalysis: reasoningData.content.scratchpad.context_analysis,
                solutionOutline: reasoningData.content.scratchpad.solution_outline,
                solutionPlan: reasoningData.content.scratchpad.solution_plan,
                response: reasoningData.content.response
            })
            .returning();

        return { 
            success: true, 
            reasoning: reasoningData.content,
            savedReasoning: newReasoning 
        };
    } catch (err: unknown) {
        console.error('Reasoning generation error:', err);
        const errorMessage = err instanceof Error ? err.message : 'Failed to generate reasoning';
        return { success: false, error: errorMessage };
    }
}
