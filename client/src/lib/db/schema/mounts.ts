import { pgTable, text, timestamp, uuid } from 'drizzle-orm/pg-core';

export const mounts = pgTable('mounts', {
	id: uuid('id').primaryKey().defaultRandom(),
	name: text('name').notNull(),
	description: text('description'),
	path: text('path').notNull(),
	type: text('type').notNull(), // e.g., 'local', could expand to other types later
	created_at: timestamp('created_at').defaultNow().notNull(),
	updated_at: timestamp('updated_at').defaultNow().notNull()
});

// Type for mount configuration
export default mounts;
export type Mount = typeof mounts.$inferSelect;
export type NewMount = typeof mounts.$inferInsert;
