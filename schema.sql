CREATE DATABASE IF NOT EXISTS feedback_system
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE feedback_system;

CREATE TABLE IF NOT EXISTS courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(120) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS feedback_questions (
    question_id INT AUTO_INCREMENT PRIMARY KEY,
    question_text VARCHAR(500) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS feedback (
    feedback_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    question_id INT NOT NULL,
    rating TINYINT NOT NULL,
    comment TEXT NULL,
    submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_feedback_course FOREIGN KEY (course_id) REFERENCES courses(course_id),
    CONSTRAINT fk_feedback_question FOREIGN KEY (question_id) REFERENCES feedback_questions(question_id),
    CONSTRAINT chk_rating_range CHECK (rating BETWEEN 1 AND 5),
    INDEX idx_feedback_course (course_id),
    INDEX idx_feedback_question (question_id),
    INDEX idx_feedback_submitted (submitted_at)
);

INSERT IGNORE INTO courses(course_name) VALUES
('Database Management Systems'), ('Python Programming'), ('Operating Systems');

INSERT IGNORE INTO feedback_questions(question_text) VALUES
('The course content is clear and well organized'),
('The teaching explains concepts effectively'),
('Learning materials are useful'),
('Questions are answered clearly'),
('Overall, I am satisfied with this course');

-- Optional demo data: run only if you want sample charts and reports.
-- These are synthetic examples, not real student feedback.
-- INSERT INTO feedback(course_id, question_id, rating, comment)
-- SELECT c.course_id, q.question_id, 4, NULL
-- FROM courses c CROSS JOIN feedback_questions q;
