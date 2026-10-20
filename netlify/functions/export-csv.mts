import type { Config } from "@netlify/functions";
import { getSummary } from "../../db/reports.js";

const cell = (value: string | number) => {
  const text = String(value);
  return /[",\n\r]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
};

export default async () => {
  try {
    const summary = await getSummary();
    const rows: (string | number)[][] = [["Report", "Category", "Average rating (1-5)", "Rating answer count"]];
    for (const c of summary.course_summary) rows.push(["Course", c.course_name, c.mean, c.count]);
    for (const q of summary.question_summary) rows.push(["Question", q.question_text, q.mean, q.count]);
    rows.push(["Overall", "Valid rating answers", "", summary.total_valid_ratings]);
    const csv = rows.map((row) => row.map(cell).join(",")).join("\r\n") + "\r\n";
    return new Response(csv, {
      headers: {
        "Content-Type": "text/csv; charset=utf-8",
        "Content-Disposition": "attachment; filename=feedback-summary.csv",
      },
    });
  } catch (error) {
    console.error(error);
    return Response.json({ error: "Database unavailable" }, { status: 503 });
  }
};

export const config: Config = { path: "/export/summary.csv", method: "GET" };
