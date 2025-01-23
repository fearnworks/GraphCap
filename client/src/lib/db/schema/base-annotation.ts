import { pgTable, text, uuid, timestamp } from 'drizzle-orm/pg-core';
import { imageInfo } from './image-info';

export const annotations = pgTable('annotations', {
	id: uuid('id').primaryKey().defaultRandom(),
	imageId: uuid('image_id')
		.notNull()
		.references(() => imageInfo.id),
	type: text('type').notNull(), // 'tag', 'caption', 'chain_of_thought'
	createdAt: timestamp('created_at').defaultNow().notNull(),
	updatedAt: timestamp('updated_at').defaultNow().notNull()
});

export default annotations;
export type Annotation = typeof annotations.$inferSelect;
export type NewAnnotation = typeof annotations.$inferInsert;
