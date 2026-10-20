import type { Config } from "@netlify/functions";
import { and, eq } from "drizzle-orm";
import { db } from "../../db/index.js";
import { courses, feedback } from "../../db/schema.js";

const back = (req: Request, status: string) => Response.redirect(new URL(`/?status=${status}`, req.url), 303);

export default async (req: Request) => {
  const form = await req.formData();
  const courseId = Number(form.get("course_id"));
  const ratings = [1, 2, 3, 4].map((i) => Number(form.get(`rating_${i}`)));
  const comment = String(form.get("comment") ?? "").trim();

  if (!Number.isInteger(courseId) || courseId < 1 || ratings.some((r) => !Number.isInteger(r))) return back(req, "missing");
  if (ratings.some((r) => r < 1 || r > 5) || comment.length > 1000) return back(req, "invalid");

  try {
    const [course] = await db
      .select({ id: courses.courseId })
      .from(courses)
      .where(and(eq(courses.courseId, courseId), eq(courses.active, true)));
    if (!course) return back(req, "course");

    // One row per question; the optional comment is stored once, on the overall-course question.
    await db.insert(feedback).values(
      ratings.map((rating, i) => ({
        courseId,
        questionId: i + 1,
        rating,
        commentOptional: i === 3 && comment ? comment : null,
      })),
    );
    return back(req, "success");
  } catch (error) {
    console.error(error);
    return back(req, "error");
  }
};

export const config: Config = { path: "/submit", method: "POST" };
