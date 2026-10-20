import type { Config } from "@netlify/functions";
import { getCourses, getQuestions } from "../../db/reports.js";

export default async () => {
  try {
    const [courses, questions] = await Promise.all([getCourses(), getQuestions()]);
    return Response.json({ courses, questions });
  } catch (error) {
    console.error(error);
    return Response.json({ error: "Database unavailable" }, { status: 503 });
  }
};

export const config: Config = { path: "/api/courses", method: "GET" };
