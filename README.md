# Student Feedback Analysis System

Beginner-friendly Flask + MySQL project for anonymous course feedback, aggregate analysis, charts and CSV export.

## Features
- Anonymous course feedback with four ratings (1–5) and optional comment.
- Server-side validation, relational MySQL schema, foreign keys and rating constraint.
- Pandas grouped summaries, NumPy dependency, three Matplotlib charts where data supports them.
- Flask JSON endpoints and aggregated CSV export.
- Small-group suppression (default minimum 5 rating answers). Comments never appear on the public dashboard.

## Run locally
Requires Python 3.10+ and MySQL 8+.
1. Create/activate a virtual environment.
2. Install: `pip install -r requirements.txt`
3. Set up schema: `mysql -u root -p < database/schema.sql`
4. Copy `.env.example` to `.env`, then configure DB variables in your terminal or environment loader. Never commit real credentials.
5. Run `python app.py`.
6. Open http://127.0.0.1:5000. Dashboard: /dashboard.

## API
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Database health |
| GET | `/api/courses` | Active courses |
| GET | `/api/summary` | Aggregate summaries |
| GET | `/export/summary.csv` | CSV report |
| GET | `/` | Feedback form |
| POST | `/submit` | Validate/store feedback |
| GET | `/dashboard` | Charts and tables |

## Database design
- `courses(course_id, course_name, active)`
- `feedback_questions(question_id, question_text)`
- `feedback(feedback_id, course_id, question_id, rating, comment_optional, submitted_at)`

Each form saves one rating row per question. Counts represent rating answers, not unique respondents. Course/question averages are arithmetic means of valid ratings. Rating distribution counts values 1 through 5.

## Privacy and limitations
Use synthetic or approved anonymized data. Do not collect names or student IDs. Comments are stored but not publicly displayed. The threshold reduces but does not guarantee anonymity. Production deployment should add admin authentication, CSRF protection, HTTPS, retention controls and rate limiting. Ratings are descriptive and do not prove teaching quality; no sentiment is inferred.

## Final demo (8–12 minutes)
Explain the problem and objectives, show schema, submit feedback, inspect records, explain dashboard charts and formulas, demonstrate API and CSV export, then cover tests and privacy limitations.

Pushing to GitHub does not itself host a live Flask/MySQL website. Deploy to a Python host and configure database credentials as environment variables to obtain a live URL.
