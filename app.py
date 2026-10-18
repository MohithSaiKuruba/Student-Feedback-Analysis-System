import csv, io, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from flask import Flask, Response, flash, jsonify, redirect, render_template, request, url_for
import mysql.connector
from mysql.connector import Error

app=Flask(__name__)
app.secret_key=os.getenv("FLASK_SECRET_KEY","local-dev-change-this")
MIN_GROUP_SIZE=int(os.getenv("MIN_GROUP_SIZE","5"))
QUESTIONS=["How clearly was the subject explained?","How well were questions answered?","How useful were the learning materials?","How would you rate the overall course?"]
def connect():
 return mysql.connector.connect(host=os.getenv("DB_HOST","localhost"),port=int(os.getenv("DB_PORT","3306")),user=os.getenv("DB_USER","root"),password=os.getenv("DB_PASSWORD",""),database=os.getenv("DB_NAME","student_feedback"))
def fetch(sql,params=()):
 conn=connect()
 try:
  cur=conn.cursor(dictionary=True);cur.execute(sql,params);return cur.fetchall()
 finally: cur.close();conn.close()
def get_courses(): return fetch("SELECT course_id,course_name FROM courses WHERE active=1 ORDER BY course_name")
def summaries():
 rows=fetch("SELECT c.course_name,q.question_text,f.rating FROM feedback f JOIN courses c ON c.course_id=f.course_id JOIN feedback_questions q ON q.question_id=f.question_id")
 df=pd.DataFrame(rows,columns=["course_name","question_text","rating"])
 if df.empty:return [],[],0,df
 df["rating"]=pd.to_numeric(df["rating"],errors="coerce");df=df[df.rating.between(1,5)]
 c=df.groupby("course_name").rating.agg(["mean","count"]).reset_index();q=df.groupby("question_text").rating.agg(["mean","count"]).reset_index()
 c=c[c["count"]>=MIN_GROUP_SIZE];q=q[q["count"]>=MIN_GROUP_SIZE];c["mean"]=c["mean"].round(2);q["mean"]=q["mean"].round(2)
 return c.to_dict("records"),q.to_dict("records"),int(len(df)),df
def make_charts(df):
 if df.empty:return []
 os.makedirs("static/charts",exist_ok=True);made=[]
 counts=df.rating.value_counts().reindex(range(1,6),fill_value=0)
 fig,ax=plt.subplots(figsize=(7,4));ax.bar(counts.index.astype(str),counts.values);ax.set(title="Overall Rating Distribution",xlabel="Rating (1 = low, 5 = high)",ylabel="Rating answers");fig.tight_layout();fig.savefig("static/charts/distribution.png",dpi=140);plt.close(fig);made.append("distribution.png")
 g=df.groupby("course_name").rating.agg(["mean","count"]);g=g[g["count"]>=MIN_GROUP_SIZE]
 if not g.empty:
  fig,ax=plt.subplots(figsize=(8,4));ax.bar(g.index,g["mean"]);ax.set(title="Average Rating by Course",xlabel="Course",ylabel="Average rating (1–5)");ax.set_ylim(0,5);ax.tick_params(axis="x",rotation=20);fig.tight_layout();fig.savefig("static/charts/courses.png",dpi=140);plt.close(fig);made.append("courses.png")
 q=df.groupby("question_text").rating.mean()
 if not q.empty:
  fig,ax=plt.subplots(figsize=(8,4));ax.barh([f"Question {i+1}" for i in range(len(q))],q.values);ax.set(title="Average Rating by Question",xlabel="Average rating (1–5)",ylabel="Question");ax.set_xlim(0,5);fig.tight_layout();fig.savefig("static/charts/questions.png",dpi=140);plt.close(fig);made.append("questions.png")
 return made
@app.get("/")
def index():
 try: cs=get_courses()
 except Error: cs=[];flash("Database unavailable. Check database/schema.sql and environment settings.","error")
 return render_template("index.html",courses=cs,questions=QUESTIONS)
@app.post("/submit")
def submit():
 try:
  cid=int(request.form.get("course_id",""));ratings=[int(request.form.get(f"rating_{i}","0")) for i in range(1,5)]
 except ValueError:
  flash("Choose a course and rate every question.","error");return redirect(url_for("index"))
 comment=request.form.get("comment","").strip()
 if any(r<1 or r>5 for r in ratings) or len(comment)>1000:
  flash("Ratings must be 1–5 and comments must be at most 1,000 characters.","error");return redirect(url_for("index"))
 try:
  if not fetch("SELECT course_id FROM courses WHERE course_id=%s AND active=1",(cid,)):
   flash("Choose a valid course.","error");return redirect(url_for("index"))
  conn=connect()
  try:
   cur=conn.cursor()
   for qid,r in enumerate(ratings,1):cur.execute("INSERT INTO feedback(course_id,question_id,rating,comment_optional) VALUES(%s,%s,%s,%s)",(cid,qid,r,comment if qid==4 and comment else None))
   conn.commit()
  finally:cur.close();conn.close()
  flash("Thanks! Your anonymous feedback was submitted.","success")
 except Error:flash("Could not save feedback. Check database settings.","error")
 return redirect(url_for("index"))
@app.get("/dashboard")
def dashboard():
 try:
  c,q,total,df=summaries();charts=make_charts(df)
  return render_template("dashboard.html",courses=c,questions=q,total=total,chart_files=charts,minimum=MIN_GROUP_SIZE)
 except Error:
  flash("Unable to load reports. Check database settings.","error")
  return render_template("dashboard.html",courses=[],questions=[],total=0,chart_files=[],minimum=MIN_GROUP_SIZE)
@app.get("/api/health")
def health():
 try:fetch("SELECT 1");return jsonify(status="ok",database="connected")
 except Error:return jsonify(status="error",database="unavailable"),503
@app.get("/api/courses")
def api_courses():
 try:return jsonify(get_courses())
 except Error:return jsonify(error="Database unavailable"),503
@app.get("/api/summary")
def api_summary():
 try:
  c,q,total,_=summaries();return jsonify(total_valid_ratings=total,minimum_group_size=MIN_GROUP_SIZE,course_summary=c,question_summary=q)
 except Error:return jsonify(error="Database unavailable"),503
@app.get("/export/summary.csv")
def export_csv():
 try:
  c,q,total,_=summaries();out=io.StringIO();w=csv.writer(out);w.writerow(["Report","Category","Average rating (1-5)","Rating answer count"])
  for x in c:w.writerow(["Course",x["course_name"],x["mean"],x["count"]])
  for x in q:w.writerow(["Question",x["question_text"],x["mean"],x["count"]])
  w.writerow(["Overall","Valid rating answers","",total])
  return Response(out.getvalue(),mimetype="text/csv",headers={"Content-Disposition":"attachment; filename=feedback-summary.csv"})
 except Error:return jsonify(error="Database unavailable"),503
@app.errorhandler(404)
def missing(_):return render_template("error.html"),404
if __name__=="__main__":app.run(host="0.0.0.0",port=int(os.getenv("PORT","5000")),debug=os.getenv("FLASK_DEBUG","false").lower()=="true")
