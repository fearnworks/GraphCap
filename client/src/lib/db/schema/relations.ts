import { relations } from 'drizzle-orm';
import {
  imageInfo,
  annotations,
  captionAnnotations,
  chainOfThoughtAnnotations,
  mounts
} from './index';

export const imageInfoRelations = relations(imageInfo, ({ one, many }) => ({
  mount: one(mounts, {
    fields: [imageInfo.mountId],
    references: [mounts.id],
  }),
  annotations: many(annotations)
}));

export const annotationRelations = relations(annotations, ({ one }) => ({
  imageInfo: one(imageInfo, {
    fields: [annotations.imageId],
    references: [imageInfo.id],
  }),
  captionAnnotation: one(captionAnnotations, {
    fields: [annotations.id],
    references: [captionAnnotations.annotationId],
  }),
  chainOfThoughtAnnotation: one(chainOfThoughtAnnotations, {
    fields: [annotations.id],
    references: [chainOfThoughtAnnotations.annotationId],
  })
})); 