# Student Feedback Analysis System

**Difficulty:** Beginner  
**Project type:** Python, Flask, MySQL, Pandas, NumPy, Matplotlib  
**Target review dates:** First review: 21–23 October 2026; final submission: 28–30 October 2026

## 1. Project Overview

The Student Feedback Analysis System collects course feedback using numeric ratings and optional comments, stores submissions, and summarizes rating patterns to help understand student satisfaction. Reports focus on aggregated results rather than identifying individual students.

## 2. Problem Statement

Feedback can be difficult to review consistently when responses are stored manually or spread across different files. This project provides a simple application and database to collect ratings, calculate course-wise summaries, compare rating distributions, and present the results through charts and exportable reports.

## 3. Objectives

- Collect course and faculty feedback through a form or API.
- Store ratings and optional comments in MySQL.
- Validate rating values and handle missing or invalid input.
- Calculate average ratings, response counts, and rating distributions by course and question.
- Visualize and compare aggregated results.
- Export summary reports for review.
- Protect privacy by preferring anonymous feedback and avoiding public display of identifiable comments.

## 4. Scope and Boundaries

### In scope
- Course and feedback-question records.
- Anonymous feedback submission.
- Numeric ratings and optional comments.
- CRUD/API operations where appropriate.
- Pandas and NumPy summary analysis.
- At least three meaningful charts when the dataset supports them.
- Aggregated report export and documented tests.

### Out of scope
- Identifying individual students from feedback.
- Publishing raw comments or identifiable submissions publicly.
- Making unsupported claims about sentiment or teaching quality.
- Using real personal or sensitive data without approval.

Use synthetic, public, anonymized, or institution-approved data. Treat any analysis as descriptive feedback, not proof of cause or professional evaluation.

## 5. Users and Features

**Suggested roles**
- **Feedback submitter:** submits a rating and optional comment without needing to provide a name.
- **Administrator/analyst:** manages courses and questions, reviews aggregate reports, and exports summaries.

**Core features**
1. Create/list/update/delete course and question records as needed.
2. Submit feedback through a form or API endpoint.
3. Validate ratings against the configured scale (recommended: integers 1–5).
4. View course-wise and question-wise average ratings and response counts.
5. Compare rating distributions across courses.
6. Generate charts and export aggregated summaries.
7. Handle empty datasets and database errors safely.

## 6. Suggested Technology Stack

- Python 3
- Flask for the web application and REST API
- MySQL for persistent storage
- Pandas for grouped summaries and data cleaning
- NumPy for averages and distributions
- Matplotlib for charts
- python-dotenv for local environment configuration
- pytest or unittest for automated tests

## 7. Database Design

### Suggested entities

- `courses(course_id, course_name)`
- `feedback_questions(question_id, question_text)`
- `feedback(feedback_id, course_id, question_id, rating, comment_optional, submitted_at)`

### Relationship sketch

```text
courses (1) -------- (many) feedback (many) -------- (1) feedback_questions
  course_id PK                 course_id FK                 question_id PK
                               question_id FK
```

### Suggested schema

```sql
CREATE DATABASE IF NOT EXISTS student_feedback;
USE student_feedback;

CREATE TABLE IF NOT EXISTS courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(150) NOT NULL UNIQUE
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
    comment_optional TEXT NULL,
    submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_feedback_course FOREIGN KEY (course_id)
        REFERENCES courses(course_id),
    CONSTRAINT fk_feedback_question FOREIGN KEY (question_id)
        REFERENCES feedback_questions(question_id),
    CONSTRAINT chk_feedback_rating CHECK (rating BETWEEN 1 AND 5)
);
```

**Database notes**
- Application-level validation must enforce the rating range even if the database version does not enforce `CHECK` constraints.
- Keep credentials in environment variables; never commit passwords or private connection strings.
- Use parameterized SQL queries.
- Add synthetic seed data for demonstration and testing.
- Consider minimum response thresholds before displaying group-level summaries.

## 8. Flask Backend and API

Suggested routes (the final implementation may adjust these):

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check application availability |
| GET | `/api/courses` | List courses |
| POST | `/api/courses` | Create a course |
| GET | `/api/questions` | List feedback questions |
| POST | `/api/questions` | Create a feedback question |
| POST | `/api/feedback` | Submit feedback |
| GET | `/api/reports/courses` | Course-wise aggregate report |
| GET | `/api/reports/questions` | Question-wise aggregate report |
| GET | `/api/reports/distribution` | Rating counts/distributions |
| GET | `/api/reports/export` | Download aggregated report, e.g. CSV |

**Validation and error handling**
- Require valid course and question IDs.
- Accept only ratings from 1 through 5.
- Treat comments as optional and apply sensible length limits.
- Return clear HTTP status codes and non-sensitive error messages.
- Handle missing records, empty results, malformed JSON, and database connection failures.
- Do not return database credentials or stack traces to users.

## 9. Data Analysis Methodology

Use only valid ratings in the configured scale. Document how missing or invalid values are handled.

For ratings (r_1, r_2, \ldots, r_n):

**Average rating**
```text
average = sum(valid ratings) / count(valid ratings)
```

**Response count**
```text
response_count = number of valid ratings in the group
```

**Rating distribution**
Count the number of valid responses for each rating (1, 2, 3, 4, 5), optionally showing percentages of valid responses.

Suggested Pandas operations include grouping by course and question, calculating `mean()` and `count()`, and using `value_counts()` for distributions. NumPy can be used for numeric averages and frequency calculations.

Report the number of responses beside each average. An average alone can hide differences in the underlying distribution. Do not infer causes or claim statistical significance without an appropriate method.

## 10. Visualizations

Include at least three useful charts when data supports them. Every chart must have a descriptive title, labelled axes, units or scale, and a short plain-language interpretation.

1. **Course-wise average rating** — bar chart; x-axis: course; y-axis: average rating (1–5).
2. **Rating distribution** — bar chart; x-axis: rating (1–5); y-axis: number of responses.
3. **Question-wise rating comparison** — grouped bar chart; x-axis: feedback question; y-axis: average rating (1–5), with courses distinguished in the legend.

Optional: response-count chart or a course-rating heatmap. Clearly label charts when there is insufficient data. Avoid displaying small-group results that could identify a respondent.

## 11. Privacy and Responsible Reporting

- Prefer anonymous submissions and do not collect names, roll numbers, email addresses, or other identifiers unless institutionally required and approved.
- Do not publish raw comments. Free-text comments can contain identifying details; restrict access, redact identifying content where appropriate, and report themes only with a documented and suitable method.
- Suppress or combine results for small groups. Choose a minimum group-size threshold with the institution/project supervisor; document the chosen threshold.
- Use synthetic or approved data for demos and screenshots.
- Do not make unsupported sentiment claims or use feedback scores as definitive proof of an instructor's performance.

## 12. Testing Plan

| Test case | Input/condition | Expected result |
|---|---|---|
| Valid feedback | Existing course/question, rating 1–5 | Saved successfully |
| Lower boundary | Rating = 1 | Accepted |
| Upper boundary | Rating = 5 | Accepted |
| Invalid low rating | Rating = 0 | Rejected with validation error |
| Invalid high rating | Rating = 6 | Rejected with validation error |
| Missing rating | Rating omitted/null | Rejected with validation error |
| Invalid foreign key | Unknown course or question ID | Rejected safely |
| Optional comment | Comment omitted | Feedback saved with NULL comment |
| Empty dataset | No feedback rows | Empty report handled without crash |
| Database unavailable | Invalid/unreachable DB connection | Safe error response; no credentials exposed |
| Aggregation | Known synthetic ratings | Average, count, and distribution match expected values |
| Privacy threshold | Group below configured minimum | Group summary suppressed or combined |

Record actual outcomes and screenshots/log evidence during testing. Do not claim tests passed until they have been run.

## 13. Standard Deliverables

### D1. Proposal and requirements
- Title, problem statement, objectives, scope, user roles, features, assumptions, and project plan.

### D2. Database design
- ER diagram or relationship sketch, schema, primary/foreign keys, sample data, data dictionary, and SQL setup script.

### D3. Flask backend
- Working application or REST APIs, CRUD operations where applicable, validation, error handling, and database connectivity.

### D4. Data analysis
- Pandas/NumPy analysis scripts, formulas, documented filters/assumptions, and summary tables.

### D5. Visualizations
- At least three meaningful charts where supported by the dataset, each with title, labelled axes, scale/units, and interpretation.

### D6. Testing
- Test cases covering normal input, invalid input, empty datasets, boundary values, and database errors, with test evidence.

### D7. Documentation
- README setup guide, project synopsis, API endpoint list, database schema, analysis methodology, screenshots/outputs, and limitations.

### D8. Final demonstration
- An 8–12 minute demonstration covering the problem, application/API, database records, analysis, charts, test results, and conclusions.

## 14. Suggested Timeline

These are relative project deadlines; the coordinator can confirm calendar dates based on the semester schedule.

| Deadline | Required submission |
|---|---|
| **Week 1 — First review: 21–23 October 2026** | Synopsis, objectives, scope, difficulty, team responsibilities, schema/ER diagram, SQL script, sample dataset, data dictionary, application structure, connection configuration, health check, and initial routes/API. |
| **Week 2 — Final submission: 28–30 October 2026** | CRUD/API operations with validation and test evidence; Pandas/NumPy analysis and summary tables; Matplotlib charts and interpretation; integrated end-to-end run; test report; README/API documentation; final synopsis; demonstration plan; source code, SQL file, charts, report, and presentation. |

## 15. Project Expo Checklist

- [ ] Submit source code, SQL schema/seed script, README, and final report before the Expo.
- [ ] Confirm the application starts and connects to MySQL on the demonstration machine.
- [ ] Configure credentials through environment variables or a local configuration file excluded from version control.
- [ ] Demonstrate one end-to-end feedback submission and its resulting aggregate analysis/chart.
- [ ] Explain chart metrics, formulas, data cleaning, and limitations in plain language.
- [ ] Be ready to explain schema design, API routes, testing, privacy protections, and division of work.
- [ ] Use synthetic, public, anonymized, or institution-approved data only.
- [ ] Do not commit passwords, real banking details, or unnecessary personal/medical information.

## 16. Setup and Configuration Expectations

The final repository should include a `.env.example` with placeholder values only, a `.gitignore` excluding `.env`, virtual environments, caches, and generated private data, plus a `requirements.txt` listing project dependencies.

Example environment variable names:

```text
DB_HOST=localhost
DB_PORT=3306
DB_NAME=student_feedback
DB_USER=your_mysql_username
DB_PASSWORD=replace_with_your_local_password
```

Never place real credentials in source code or commit the actual `.env` file.

## 17. Expected Outputs

- Course-wise feedback report.
- Average rating by course and question.
- Response counts and rating distributions.
- At least three labelled rating charts, where the dataset supports them.
- CSV or similar export of aggregated summaries.
- Documented test results and an 8–12 minute demonstration.

## 18. Limitations

- Results depend on the number and representativeness of responses.
- Small samples may not represent all students; response counts should accompany averages.
- Ratings describe submitted feedback and do not establish why a course received a score.
- Optional comments may contain identifying information and require careful handling.
- The system is an educational project, not a validated institutional evaluation tool.
