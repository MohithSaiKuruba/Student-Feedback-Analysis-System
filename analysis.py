"""Generate aggregate CSV reports and three charts from a MySQL feedback database."""
import os
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mysql.connector
from dotenv import load_dotenv

load_dotenv()
OUTPUT_DIR = Path("reports")
OUTPUT_DIR.mkdir(exist_ok=True)

def load_feedback():
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME", "feedback_system"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "")
    )
    try:
        return pd.read_sql("""
            SELECT c.course_name, q.question_text, f.rating, f.submitted_at
            FROM feedback f
            JOIN courses c ON c.course_id=f.course_id
            JOIN feedback_questions q ON q.question_id=f.question_id
        """, connection)
    finally:
        connection.close()

def main():
    df = load_feedback()
    if df.empty:
        print("No feedback rows found. Submit feedback or add synthetic demo rows first.")
        return
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df = df.dropna(subset=["rating"])
    min_group_size = int(os.getenv("MIN_GROUP_SIZE", "5"))

    course = df.groupby("course_name").agg(
        response_count=("rating", "count"), average_rating=("rating", "mean")
    ).reset_index()
    course["average_rating"] = course["average_rating"].round(2)
    course.loc[course["response_count"] < min_group_size, "average_rating"] = pd.NA
    course.to_csv(OUTPUT_DIR / "course_summary.csv", index=False)

    question = df.groupby("question_text").agg(
        response_count=("rating", "count"), average_rating=("rating", "mean")
    ).reset_index()
    question["average_rating"] = question["average_rating"].round(2)
    question.loc[question["response_count"] < min_group_size, "average_rating"] = pd.NA
    question.to_csv(OUTPUT_DIR / "question_summary.csv", index=False)

    # Chart 1: average rating by course (only groups meeting privacy threshold).
    visible = course.dropna(subset=["average_rating"])
    if not visible.empty:
        plt.figure(figsize=(9, 5))
        plt.bar(visible["course_name"], visible["average_rating"])
        plt.ylim(0, 5)
        plt.ylabel("Average rating (1–5)")
        plt.title("Average Course Ratings")
        plt.xticks(rotation=20, ha="right")
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "average_by_course.png", dpi=150)
        plt.close()

    # Chart 2: rating distribution, suppressed if the overall dataset is too small.
    if len(df) >= min_group_size:
        counts = df["rating"].value_counts().reindex([1, 2, 3, 4, 5], fill_value=0)
        plt.figure(figsize=(7, 5))
        plt.bar(counts.index.astype(str), counts.values)
        plt.xlabel("Rating")
        plt.ylabel("Number of responses")
        plt.title("Feedback Rating Distribution")
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "rating_distribution.png", dpi=150)
        plt.close()

    # Chart 3: question averages, visible only for sufficiently large groups.
    visible_q = question.dropna(subset=["average_rating"])
    if not visible_q.empty:
        plt.figure(figsize=(10, 6))
        plt.barh(visible_q["question_text"], visible_q["average_rating"])
        plt.xlim(0, 5)
        plt.xlabel("Average rating (1–5)")
        plt.title("Average Rating by Question")
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "average_by_question.png", dpi=150)
        plt.close()

    print(f"Reports saved in {OUTPUT_DIR.resolve()}")
    print("CSV exports contain aggregate data only; individual comments are never exported.")

if __name__ == "__main__":
    main()
