# User Guide

## Student workflow
1. Open the app homepage.
2. Choose a course and a feedback question.
3. Select a rating from 1 (Poor) to 5 (Excellent).
4. Optionally enter a short comment without names or identifying details.
5. Select **Submit feedback**. No student identity field is collected.

## Admin/developer workflow
1. Create or edit courses and questions with the API.
2. Review aggregate reports at `/api/reports/courses`, `/api/reports/questions`, and `/api/reports/distribution`.
3. Download aggregate CSV from `/api/reports/export`.
4. Run `python analysis.py` to create charts and summary CSVs in `reports/`.

## Example API calls

Add a course:

```bash
curl -X POST http://127.0.0.1:5000/api/courses -H "Content-Type: application/json" -d "{\"course_name\":\"Java Programming\"}"
```

Submit feedback (replace IDs with values returned by the course and question endpoints):

```bash
curl -X POST http://127.0.0.1:5000/api/feedback -H "Content-Type: application/json" -d "{\"course_id\":1,\"question_id\":1,\"rating\":4,\"comment\":\"Clear explanation\"}"
```

## Troubleshooting
- **Database unavailable:** confirm MySQL is running, the database was created using `schema.sql`, and `.env` has correct credentials.
- **No courses/questions in the form:** check `/api/courses` and `/api/questions` in the browser.
- **No charts created:** submit enough feedback to meet `MIN_GROUP_SIZE`; small groups are intentionally suppressed.
- **Module not found:** activate the virtual environment and run `pip install -r requirements.txt`.
