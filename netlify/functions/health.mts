import type { Config } from "@netlify/functions";
import { sql } from "drizzle-orm";
import { db } from "../../db/index.js";

export default async () => {
  try {
    await db.execute(sql`SELECT 1`);
    return Response.json({ status: "ok", database: "connected" });
  } catch (error) {
    console.error(error);
    return Response.json({ status: "error", database: "unavailable" }, { status: 503 });
  }
};

export const config: Config = { path: "/api/health", method: "GET" };
