-- Seed the course list and the four feedback questions.
INSERT INTO "courses" ("course_name") VALUES
  ('Python Programming'),
  ('Database Management Systems'),
  ('Java Programming'),
  ('Web Development')
ON CONFLICT ("course_name") DO NOTHING;
--> statement-breakpoint
INSERT INTO "feedback_questions" ("question_id", "question_text") VALUES
  (1, 'How clearly was the subject explained?'),
  (2, 'How well were questions answered?'),
  (3, 'How useful were the learning materials?'),
  (4, 'How would you rate the overall course?')
ON CONFLICT ("question_id") DO NOTHING;
