"""Insert synthetic demonstration ratings; never use real student identities."""
import os, random
import mysql.connector
random.seed(42)
conn=mysql.connector.connect(host=os.getenv("DB_HOST","localhost"),port=int(os.getenv("DB_PORT","3306")),user=os.getenv("DB_USER","root"),password=os.getenv("DB_PASSWORD",""),database=os.getenv("DB_NAME","student_feedback"))
try:
 cur=conn.cursor()
 cur.execute("SELECT course_id FROM courses WHERE active=1");courses=[r[0] for r in cur.fetchall()]
 cur.execute("SELECT question_id FROM feedback_questions");questions=[r[0] for r in cur.fetchall()]
 for cid in courses:
  for _ in range(12):
   base=random.choice([3,4,4,5])
   for qid in questions:
    rating=max(1,min(5,base+random.choice([-1,0,0,0,1])))
    cur.execute("INSERT INTO feedback(course_id,question_id,rating) VALUES(%s,%s,%s)",(cid,qid,rating))
 conn.commit();print("Synthetic demo ratings inserted.")
finally:cur.close();conn.close()
