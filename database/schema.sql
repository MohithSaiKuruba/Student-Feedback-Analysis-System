CREATE DATABASE IF NOT EXISTS student_feedback CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE student_feedback;
CREATE TABLE IF NOT EXISTS courses (course_id INT AUTO_INCREMENT PRIMARY KEY, course_name VARCHAR(150) NOT NULL UNIQUE, active BOOLEAN NOT NULL DEFAULT TRUE);
CREATE TABLE IF NOT EXISTS feedback_questions (question_id INT AUTO_INCREMENT PRIMARY KEY, question_text VARCHAR(255) NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS feedback (feedback_id BIGINT AUTO_INCREMENT PRIMARY KEY, course_id INT NOT NULL, question_id INT NOT NULL, rating TINYINT NOT NULL, comment_optional VARCHAR(1000) NULL, submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, CONSTRAINT fk_feedback_course FOREIGN KEY (course_id) REFERENCES courses(course_id), CONSTRAINT fk_feedback_question FOREIGN KEY (question_id) REFERENCES feedback_questions(question_id), CONSTRAINT chk_rating CHECK (rating BETWEEN 1 AND 5), INDEX idx_feedback_course(course_id), INDEX idx_feedback_question(question_id));
INSERT IGNORE INTO courses(course_name) VALUES ('Python Programming'),('Database Management Systems'),('Java Programming'),('Web Development');
INSERT IGNORE INTO feedback_questions(question_id,question_text) VALUES (1,'How clearly was the subject explained?'),(2,'How well were questions answered?'),(3,'How useful were the learning materials?'),(4,'How would you rate the overall course?');
-- Optional least-privilege account: CREATE USER 'feedback_app'@'localhost' IDENTIFIED BY 'replace-me';
-- GRANT SELECT, INSERT ON student_feedback.* TO 'feedback_app'@'localhost';
