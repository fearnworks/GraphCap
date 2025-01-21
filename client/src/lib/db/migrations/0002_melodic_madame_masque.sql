CREATE TABLE IF NOT EXISTS "annotations" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"image_id" uuid NOT NULL,
	"type" text NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "caption_annotations" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"annotation_id" uuid NOT NULL,
	"short_caption" text NOT NULL,
	"verification" text NOT NULL,
	"dense_caption" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "chain_of_thought_annotations" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"annotation_id" uuid NOT NULL,
	"problem_analysis" text NOT NULL,
	"context_analysis" text NOT NULL,
	"solution_outline" text NOT NULL,
	"solution_plan" text NOT NULL,
	"response" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "image_info" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"hash" text NOT NULL,
	"mount_id" uuid NOT NULL,
	"relative_path" text NOT NULL,
	"file_size" integer NOT NULL,
	"width" integer NOT NULL,
	"height" integer NOT NULL,
	"mime_type" text NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "tag_annotations" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"annotation_id" uuid NOT NULL,
	"category" text NOT NULL,
	"tag" text NOT NULL,
	"confidence" numeric(5, 4) NOT NULL
);
--> statement-breakpoint
DROP TABLE "chain_of_thought" CASCADE;--> statement-breakpoint
DROP TABLE "image_data" CASCADE;--> statement-breakpoint
DROP TABLE "image_tag" CASCADE;--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "annotations" ADD CONSTRAINT "annotations_image_id_image_info_id_fk" FOREIGN KEY ("image_id") REFERENCES "public"."image_info"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "caption_annotations" ADD CONSTRAINT "caption_annotations_annotation_id_annotations_id_fk" FOREIGN KEY ("annotation_id") REFERENCES "public"."annotations"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "chain_of_thought_annotations" ADD CONSTRAINT "chain_of_thought_annotations_annotation_id_annotations_id_fk" FOREIGN KEY ("annotation_id") REFERENCES "public"."annotations"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "image_info" ADD CONSTRAINT "image_info_mount_id_mounts_id_fk" FOREIGN KEY ("mount_id") REFERENCES "public"."mounts"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "tag_annotations" ADD CONSTRAINT "tag_annotations_annotation_id_annotations_id_fk" FOREIGN KEY ("annotation_id") REFERENCES "public"."annotations"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
