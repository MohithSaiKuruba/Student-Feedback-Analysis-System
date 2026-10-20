import { sql } from "drizzle-orm";
import { boolean, check, index, integer, pgTable, serial, smallint, timestamp, varchar, bigserial } from "drizzle-orm/pg-core";

export const courses = pgTable("courses", {
  courseId: serial("course_id").primaryKey(),
  courseName: varchar("course_name", { length: 150 }).notNull().unique(),
  active: boolean().notNull().default(true),
});

export const feedbackQuestions = pgTable("feedback_questions", {
  questionId: integer("question_id").primaryKey(),
  questionText: varchar("question_text", { length: 255 }).notNull().unique(),
});

export const feedback = pgTable(
  "feedback",
  {
    feedbackId: bigserial("feedback_id", { mode: "number" }).primaryKey(),
    courseId: integer("course_id").notNull().references(() => courses.courseId),
    questionId: integer("question_id").notNull().references(() => feedbackQuestions.questionId),
    rating: smallint().notNull(),
    commentOptional: varchar("comment_optional", { length: 1000 }),
    submittedAt: timestamp("submitted_at").notNull().defaultNow(),
  },
  (t) => [
    check("chk_rating", sql`${t.rating} BETWEEN 1 AND 5`),
    index("idx_feedback_course").on(t.courseId),
    index("idx_feedback_question").on(t.questionId),
  ],
);
