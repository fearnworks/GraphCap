CREATE TABLE IF NOT EXISTS "chain_of_thought" (
	"id" serial PRIMARY KEY NOT NULL,
	"problem_analysis" text NOT NULL,
	"context_analysis" text NOT NULL,
	"solution_outline" text NOT NULL,
	"solution_plan" text NOT NULL,
	"response" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "image_data" (
	"id" serial PRIMARY KEY NOT NULL,
	"short_caption" text NOT NULL,
	"verification" text NOT NULL,
	"dense_caption" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "image_tag" (
	"id" serial PRIMARY KEY NOT NULL,
	"category" varchar(50) NOT NULL,
	"tag" varchar(255) NOT NULL,
	"confidence" numeric(5, 4) NOT NULL,
	"image_data_id" integer NOT NULL
);
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "image_tag" ADD CONSTRAINT "image_tag_image_data_id_image_data_id_fk" FOREIGN KEY ("image_data_id") REFERENCES "public"."image_data"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
