DROP TABLE "tag_annotations" CASCADE;--> statement-breakpoint
ALTER TABLE "caption_annotations" ADD COLUMN "tags" jsonb;