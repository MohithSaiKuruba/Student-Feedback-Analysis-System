import { asc, avg, count, eq, sql } from "drizzle-orm";
import { db } from "./index.js";
import { courses, feedback, feedbackQuestions } from "./schema.js";

export const minGroupSize = () => Number.parseInt(Netlify.env.get("MIN_GROUP_SIZE") ?? "5", 10) || 5;

export const getCourses = () =>
  db
    .select({ course_id: courses.courseId, course_name: courses.courseName })
    .from(courses)
    .where(eq(courses.active, true))
    .orderBy(asc(courses.courseName));

export const getQuestions = () =>
  db
    .select({ question_id: feedbackQuestions.questionId, question_text: feedbackQuestions.questionText })
    .from(feedbackQuestions)
    .orderBy(asc(feedbackQuestions.questionId));

const validRating = sql`${feedback.rating} BETWEEN 1 AND 5`;
const round2 = (value: string | null) => Math.round(Number(value) * 100) / 100;

// Aggregates only: groups smaller than the minimum size are suppressed and comments are never returned.
export async function getSummary() {
  const minimum = minGroupSize();

  const courseRows = await db
    .select({ course_name: courses.courseName, mean: avg(feedback.rating), count: count() })
    .from(feedback)
    .innerJoin(courses, eq(courses.courseId, feedback.courseId))
    .where(validRating)
    .groupBy(courses.courseName)
    .orderBy(asc(courses.courseName));

  const questionRows = await db
    .select({ question_id: feedbackQuestions.questionId, question_text: feedbackQuestions.questionText, mean: avg(feedback.rating), count: count() })
    .from(feedback)
    .innerJoin(feedbackQuestions, eq(feedbackQuestions.questionId, feedback.questionId))
    .where(validRating)
    .groupBy(feedbackQuestions.questionId, feedbackQuestions.questionText)
    .orderBy(asc(feedbackQuestions.questionId));

  const distributionRows = await db
    .select({ rating: feedback.rating, count: count() })
    .from(feedback)
    .where(validRating)
    .groupBy(feedback.rating);

  const total = distributionRows.reduce((sum, row) => sum + row.count, 0);
  const distribution = [1, 2, 3, 4, 5].map((rating) => ({
    rating,
    count: distributionRows.find((row) => row.rating === rating)?.count ?? 0,
  }));

  return {
    total_valid_ratings: total,
    minimum_group_size: minimum,
    course_summary: courseRows.filter((r) => r.count >= minimum).map((r) => ({ course_name: r.course_name, mean: round2(r.mean), count: r.count })),
    question_summary: questionRows.filter((r) => r.count >= minimum).map((r) => ({ question_id: r.question_id, question_text: r.question_text, mean: round2(r.mean), count: r.count })),
    rating_distribution: total >= minimum ? distribution : [],
  };
}
