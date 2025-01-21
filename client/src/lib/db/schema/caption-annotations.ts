import { pgTable, text, uuid, jsonb } from 'drizzle-orm/pg-core';
import { annotations } from './index';

export enum TagType {
  ENTITY = "Entity",
  RELATIONSHIP = "Relationship",
  STYLE = "Style",
  ATTRIBUTE = "Attribute",
  COMPOSITION = "Composition",
  CONTEXTUAL = "Contextual",
  TECHNICAL = "Technical",
  SEMANTIC = "Semantic"
}

export interface ImageTag {
  category: TagType;
  tag: string;
  confidence: number;
}

export const captionAnnotations = pgTable('caption_annotations', {
  id: uuid('id').primaryKey().defaultRandom(),
  annotationId: uuid('annotation_id')
    .notNull()
    .references(() => annotations.id),
  shortCaption: text('short_caption').notNull(),
  verification: text('verification').notNull(),
  denseCaption: text('dense_caption').notNull(),
  tags: jsonb('tags').$type<ImageTag[]>()
});

export default captionAnnotations;
export type CaptionAnnotation = typeof captionAnnotations.$inferSelect;
export type NewCaptionAnnotation = typeof captionAnnotations.$inferInsert; 