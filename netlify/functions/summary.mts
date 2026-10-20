import type { Config } from "@netlify/functions";
import { getSummary } from "../../db/reports.js";

export default async () => {
  try {
    return Response.json(await getSummary());
  } catch (error) {
    console.error(error);
    return Response.json({ error: "Database unavailable" }, { status: 503 });
  }
};

export const config: Config = { path: "/api/summary", method: "GET" };
