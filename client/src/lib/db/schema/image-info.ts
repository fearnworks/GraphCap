import { pgTable, text, uuid, integer, timestamp } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';
import { mounts } from './mounts';
import { annotations } from './annotations';

export const imageInfo = pgTable('image_info', {
  id: uuid('id').primaryKey().defaultRandom(),
  hash: text('hash').notNull(),
  mountId: uuid('mount_id')
    .notNull()
    .references(() => mounts.id),
  relativePath: text('relative_path').notNull(),
  fileSize: integer('file_size').notNull(),
  width: integer('width').notNull(),
  height: integer('height').notNull(),
  mimeType: text('mime_type').notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull()
});

export const imageInfoRelations = relations(imageInfo, ({ one, many }) => ({
    mount: one(mounts, {
        fields: [imageInfo.mountId],
        references: [mounts.id],
    }),
    annotations: many(annotations)
}));

export default imageInfo;
export type ImageInfo = typeof imageInfo.$inferSelect;
export type NewImageInfo = typeof imageInfo.$inferInsert; 