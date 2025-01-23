import { pgTable, text, uuid, numeric, timestamp } from 'drizzle-orm/pg-core';
import { imageInfo } from './image-info';

// Base annotation table
export const annotations = pgTable('annotations', {
	id: uuid('id').primaryKey().defaultRandom(),
	imageId: uuid('image_id')
		.notNull()
		.references(() => imageInfo.id),
	type: text('type').notNull(), // 'tag', 'caption', 'chain_of_thought'
	createdAt: timestamp('created_at').defaultNow().notNull(),
	updatedAt: timestamp('updated_at').defaultNow().notNull()
});

// Tag annotations
export const tagAnnotations = pgTable('tag_annotations', {
	id: uuid('id').primaryKey().defaultRandom(),
	annotationId: uuid('annotation_id')
		.notNull()
		.references(() => annotations.id),
	category: text('category').notNull(), // Enum values from TagCategory
	tag: text('tag').notNull(),
	confidence: numeric('confidence', { precision: 5, scale: 4 }).notNull()
});

// Caption annotations
export const captionAnnotations = pgTable('caption_annotations', {
	id: uuid('id').primaryKey().defaultRandom(),
	annotationId: uuid('annotation_id')
		.notNull()
		.references(() => annotations.id),
	shortCaption: text('short_caption').notNull(),
	verification: text('verification').notNull(),
	denseCaption: text('dense_caption').notNull()
});

// Chain of thought annotations
export const chainOfThoughtAnnotations = pgTable('chain_of_thought_annotations', {
	id: uuid('id').primaryKey().defaultRandom(),
	annotationId: uuid('annotation_id')
		.notNull()
		.references(() => annotations.id),
	problemAnalysis: text('problem_analysis').notNull(),
	contextAnalysis: text('context_analysis').notNull(),
	solutionOutline: text('solution_outline').notNull(),
	solutionPlan: text('solution_plan').notNull(),
	response: text('response').notNull()
});

export type Annotation = typeof annotations.$inferSelect;
export type NewAnnotation = typeof annotations.$inferInsert;
export type TagAnnotation = typeof tagAnnotations.$inferSelect;
export type CaptionAnnotation = typeof captionAnnotations.$inferSelect;
export type ChainOfThoughtAnnotation = typeof chainOfThoughtAnnotations.$inferSelect;
