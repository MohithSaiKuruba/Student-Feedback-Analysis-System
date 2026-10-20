CREATE TABLE "courses" (
	"course_id" serial PRIMARY KEY,
	"course_name" varchar(150) NOT NULL UNIQUE,
	"active" boolean DEFAULT true NOT NULL
);
--> statement-breakpoint
CREATE TABLE "feedback" (
	"feedback_id" bigserial PRIMARY KEY,
	"course_id" integer NOT NULL,
	"question_id" integer NOT NULL,
	"rating" smallint NOT NULL,
	"comment_optional" varchar(1000),
	"submitted_at" timestamp DEFAULT now() NOT NULL,
	CONSTRAINT "chk_rating" CHECK ("rating" BETWEEN 1 AND 5)
);
--> statement-breakpoint
CREATE TABLE "feedback_questions" (
	"question_id" integer PRIMARY KEY,
	"question_text" varchar(255) NOT NULL UNIQUE
);
--> statement-breakpoint
CREATE INDEX "idx_feedback_course" ON "feedback" ("course_id");--> statement-breakpoint
CREATE INDEX "idx_feedback_question" ON "feedback" ("question_id");--> statement-breakpoint
ALTER TABLE "feedback" ADD CONSTRAINT "feedback_course_id_courses_course_id_fkey" FOREIGN KEY ("course_id") REFERENCES "courses"("course_id");--> statement-breakpoint
ALTER TABLE "feedback" ADD CONSTRAINT "feedback_question_id_feedback_questions_question_id_fkey" FOREIGN KEY ("question_id") REFERENCES "feedback_questions"("question_id");