import { pgTable, text, uuid } from 'drizzle-orm/pg-core';
import { annotations } from './index';

export const chainOfThoughtAnnotations = pgTable('chain_of_thought_annotations', {
  id: uuid('id').primaryKey().defaultRandom(),
  annotationId: uuid('annotation_id')
    .notNull()
    .references(() => annotations.id),
  question: text('question'),
  problemAnalysis: text('problem_analysis').notNull(),
  contextAnalysis: text('context_analysis').notNull(),
  solutionOutline: text('solution_outline').notNull(),
  solutionPlan: text('solution_plan').notNull(),
  response: text('response').notNull()
});

export default chainOfThoughtAnnotations;
export type ChainOfThoughtAnnotation = typeof chainOfThoughtAnnotations.$inferSelect;
export type NewChainOfThoughtAnnotation = typeof chainOfThoughtAnnotations.$inferInsert; 