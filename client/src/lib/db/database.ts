import { db } from './index';
import { imageDataTable, imageTagTable, chainOfThoughtTable } from './schema/index';
import type { ImageData } from '$lib/graphcaps';
import { eq } from 'drizzle-orm';

export async function saveCaption(captionData: ImageData) {
	const [imageDataEntry] = await db
		.insert(imageDataTable)
		.values({
			shortCaption: captionData.short_caption,
			denseCaption: captionData.dense_caption,
			verification: captionData.verification
		})
		.returning();

	const tagValues = captionData.tags_list.map((tag) => ({
		imageDataId: imageDataEntry.id,
		category: tag.category,
		tag: tag.tag,
		confidence: tag.confidence
	}));

	const savedTags = await db
		.insert(imageTagTable)
		.values(
			tagValues.map((tag) => ({
				...tag,
				confidence: tag.confidence.toString()
			}))
		)
		.returning();

	return {
		...imageDataEntry,
		tags: savedTags
	};
}

export async function getImageWithCaption(imageId: number) {
	const result = await db.query.imageDataTable.findFirst({
		where: eq(imageDataTable.id, imageId),
		with: {
			tags: true
		}
	});

	if (!result) return null;

	return result;
}

export async function getAllImages() {
	return db.query.imageDataTable.findMany({
		with: {
			tags: true
		},
		orderBy: (imgs, { desc }) => [desc(imgs.id)]
	});
}

export async function saveChainOfThought(data: {
	problemAnalysis: string;
	contextAnalysis: string;
	solutionOutline: string;
	solutionPlan: string;
	response: string;
}) {
	const [result] = await db.insert(chainOfThoughtTable).values(data).returning();

	return result;
}

export async function getChainOfThought(id: number) {
	return db.query.chainOfThoughtTable.findFirst({
		where: eq(chainOfThoughtTable.id, id)
	});
}
