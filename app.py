import os
import io
import csv
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string, Response
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

load_dotenv()
app = Flask(__name__)
MIN_GROUP_SIZE = int(os.getenv("MIN_GROUP_SIZE", "5"))

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME", "feedback_system"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "")
    )

def query_db(sql, params=(), fetch=True):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(sql, params)
        result = cursor.fetchall() if fetch else None
        if not fetch:
            connection.commit()
            result = {"id": cursor.lastrowid, "affected_rows": cursor.rowcount}
        return result
    finally:
        cursor.close()
        connection.close()

def error_response(message, status=400):
    return jsonify({"error": message}), status

HOME = """
<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Student Feedback Analysis System</title>
<style>
body{font-family:Arial,sans-serif;background:#f3f6fb;color:#172033;margin:0}
header{background:#183b66;color:white;padding:28px 6%}main{max-width:900px;margin:28px auto;padding:0 16px}
.card{background:white;border-radius:12px;padding:22px;margin:16px 0;box-shadow:0 3px 14px #15233a12}
label{display:block;margin:12px 0 6px;font-weight:bold}select,input,textarea{box-sizing:border-box;width:100%;padding:11px;border:1px solid #ccd3df;border-radius:7px}
button{background:#1769aa;color:white;border:0;padding:12px 18px;border-radius:7px;cursor:pointer;margin-top:14px}
small{color:#526078}.links a{margin-right:14px;color:#1769aa}
</style></head><body><header><h1>Student Feedback Analysis System</h1>
<p>Share course feedback anonymously and help improve teaching quality.</p></header><main>
<div class="card"><h2>Submit feedback</h2><p>Your submission does not ask for your name or student ID.</p>
<form id="feedbackForm">
<label for="course">Course</label><select id="course" required><option value="">Loading courses…</option></select>
<label for="question">Feedback question</label><select id="question" required><option value="">Loading questions…</option></select>
<label for="rating">Rating (1 = Poor, 5 = Excellent)</label><select id="rating" required>
<option value="">Choose a rating</option><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5</option></select>
<label for="comment">Optional comment</label><textarea id="comment" maxlength="1000" rows="3" placeholder="Please do not include names or personal details"></textarea>
<button type="submit">Submit feedback</button><p id="message" role="status"></p></form></div>
<div class="card"><h2>Reports</h2><p>Reports show aggregated ratings only. Small groups may be hidden to protect privacy.</p>
<div class="links"><a href="/api/reports/courses">Course report (JSON)</a><a href="/api/reports/questions">Question report (JSON)</a>
<a href="/api/reports/distribution">Rating distribution (JSON)</a><a href="/api/reports/export">Download aggregate CSV</a></div>
</div><small>Demo project · Flask + MySQL · Ratings are not verified claims about individual faculty.</small></main>
<script>
async function loadOptions(url,id,label){const r=await fetch(url);const d=await r.json();const el=document.getElementById(id);el.innerHTML='<option value="">Choose '+label+'</option>';if(!r.ok){el.innerHTML='<option value="">Could not load options</option>';return;}d.forEach(x=>{const o=document.createElement('option');o.value=x[id==='course'?'course_id':'question_id'];o.textContent=x[id==='course'?'course_name':'question_text'];el.appendChild(o);});}
loadOptions('/api/courses','course','a course');loadOptions('/api/questions','question','a question');
document.getElementById('feedbackForm').addEventListener('submit',async e=>{e.preventDefault();const message=document.getElementById('message');message.textContent='Submitting…';const payload={course_id:Number(document.getElementById('course').value),question_id:Number(document.getElementById('question').value),rating:Number(document.getElementById('rating').value),comment:document.getElementById('comment').value};try{const r=await fetch('/api/feedback',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const d=await r.json();message.textContent=r.ok?'Thank you! Feedback submitted anonymously.':(d.error||'Submission failed.');if(r.ok)e.target.reset();}catch(err){message.textContent='Could not contact the server. Please try again.';}});
</script></body></html>
"""

@app.get("/")
def home():
    return render_template_string(HOME)

@app.get("/health")
def health():
    try:
        query_db("SELECT 1 AS ok")
        return jsonify({"status": "ok", "database": "connected"})
    except Error:
        return jsonify({"status": "error", "database": "unavailable"}), 503

@app.get("/api/courses")
def get_courses():
    try:
        return jsonify(query_db("SELECT course_id, course_name FROM courses ORDER BY course_name"))
    except Error:
        return error_response("Database unavailable. Run schema.sql and check your .env settings.", 503)

@app.post("/api/courses")
def add_course():
    data = request.get_json(silent=True) or {}
    name = str(data.get("course_name", "")).strip()
    if not name or len(name) > 120:
        return error_response("course_name is required and must be at most 120 characters.")
    try:
        result = query_db("INSERT INTO courses(course_name) VALUES (%s)", (name,), fetch=False)
        return jsonify({"message": "Course created", "course_id": result["id"], "course_name": name}), 201
    except Error as exc:
        if getattr(exc, "errno", None) == 1062:
            return error_response("That course already exists.", 409)
        return error_response("Could not save course. Check database settings.", 503)

@app.get("/api/questions")
def get_questions():
    try:
        return jsonify(query_db("SELECT question_id, question_text FROM feedback_questions ORDER BY question_id"))
    except Error:
        return error_response("Database unavailable. Run schema.sql and check your .env settings.", 503)

@app.post("/api/questions")
def add_question():
    data = request.get_json(silent=True) or {}
    question = str(data.get("question_text", "")).strip()
    if not question or len(question) > 500:
        return error_response("question_text is required and must be at most 500 characters.")
    try:
        result = query_db("INSERT INTO feedback_questions(question_text) VALUES (%s)", (question,), fetch=False)
        return jsonify({"message": "Question created", "question_id": result["id"], "question_text": question}), 201
    except Error as exc:
        if getattr(exc, "errno", None) == 1062:
            return error_response("That question already exists.", 409)
        return error_response("Could not save question. Check database settings.", 503)

@app.post("/api/feedback")
def submit_feedback():
    data = request.get_json(silent=True) or {}
    try:
        course_id = int(data.get("course_id"))
        question_id = int(data.get("question_id"))
        rating = int(data.get("rating"))
    except (TypeError, ValueError):
        return error_response("course_id, question_id and rating must be valid integers.")
    if rating < 1 or rating > 5:
        return error_response("rating must be between 1 and 5.")
    comment = str(data.get("comment") or "").strip()
    if len(comment) > 1000:
        return error_response("comment must be at most 1000 characters.")
    try:
        exists = query_db("SELECT course_id FROM courses WHERE course_id=%s", (course_id,))
        q_exists = query_db("SELECT question_id FROM feedback_questions WHERE question_id=%s", (question_id,))
        if not exists or not q_exists:
            return error_response("Selected course or question does not exist.", 404)
        result = query_db(
            "INSERT INTO feedback(course_id, question_id, rating, comment) VALUES (%s,%s,%s,%s)",
            (course_id, question_id, rating, comment or None), fetch=False)
        return jsonify({"message": "Feedback submitted", "feedback_id": result["id"]}), 201
    except Error:
        return error_response("Could not save feedback. Check the database connection.", 503)

@app.get("/api/reports/courses")
def course_report():
    try:
        rows = query_db("""
            SELECT c.course_id, c.course_name, COUNT(f.feedback_id) AS response_count,
                   ROUND(AVG(f.rating), 2) AS average_rating
            FROM courses c LEFT JOIN feedback f ON c.course_id=f.course_id
            GROUP BY c.course_id, c.course_name ORDER BY c.course_name
        """)
        return jsonify([r if r["response_count"] >= MIN_GROUP_SIZE else {
            "course_id": r["course_id"], "course_name": r["course_name"],
            "response_count": r["response_count"], "average_rating": None,
            "suppressed": True
        } for r in rows])
    except Error:
        return error_response("Could not generate report.", 503)

@app.get("/api/reports/questions")
def question_report():
    try:
        rows = query_db("""
            SELECT q.question_id, q.question_text, COUNT(f.feedback_id) AS response_count,
                   ROUND(AVG(f.rating), 2) AS average_rating
            FROM feedback_questions q LEFT JOIN feedback f ON q.question_id=f.question_id
            GROUP BY q.question_id, q.question_text ORDER BY q.question_id
        """)
        return jsonify([r if r["response_count"] >= MIN_GROUP_SIZE else {
            "question_id": r["question_id"], "question_text": r["question_text"],
            "response_count": r["response_count"], "average_rating": None,
            "suppressed": True
        } for r in rows])
    except Error:
        return error_response("Could not generate report.", 503)

@app.get("/api/reports/distribution")
def rating_distribution():
    try:
        rows = query_db("SELECT rating, COUNT(*) AS response_count FROM feedback GROUP BY rating ORDER BY rating")
        total = sum(row["response_count"] for row in rows)
        return jsonify({"total_responses": total, "distribution": rows if total >= MIN_GROUP_SIZE else [],
                        "suppressed": total < MIN_GROUP_SIZE})
    except Error:
        return error_response("Could not generate report.", 503)

@app.get("/api/reports/export")
def export_report():
    try:
        rows = query_db("""
            SELECT c.course_name, q.question_text, COUNT(f.feedback_id) AS response_count,
                   ROUND(AVG(f.rating), 2) AS average_rating
            FROM courses c CROSS JOIN feedback_questions q
            LEFT JOIN feedback f ON f.course_id=c.course_id AND f.question_id=q.question_id
            GROUP BY c.course_name, q.question_text ORDER BY c.course_name, q.question_id
        """)
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["course_name", "question_text", "response_count", "average_rating"])
        writer.writeheader()
        for row in rows:
            if row["response_count"] >= MIN_GROUP_SIZE:
                writer.writerow(row)
            else:
                writer.writerow({"course_name": row["course_name"], "question_text": row["question_text"],
                                 "response_count": "SUPPRESSED", "average_rating": "SUPPRESSED"})
        return Response(output.getvalue(), mimetype="text/csv",
                        headers={"Content-Disposition": "attachment; filename=feedback_aggregate_report.csv"})
    except Error:
        return error_response("Could not export report.", 503)

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
            host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
