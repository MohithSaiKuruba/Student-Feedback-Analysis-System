"""Fast tests for request validation; these do not require a running MySQL server."""
import importlib.util
from pathlib import Path
import pytest

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"
spec = importlib.util.spec_from_file_location("feedback_app", APP_PATH)
feedback_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(feedback_app)
client = feedback_app.app.test_client()

def test_feedback_rejects_non_integer_fields():
    response = client.post("/api/feedback", json={"course_id": "abc", "question_id": 1, "rating": 3})
    assert response.status_code == 400
    assert "integers" in response.get_json()["error"]

@pytest.mark.parametrize("rating", [0, 6, -1, 10])
def test_feedback_rejects_rating_outside_range(rating):
    response = client.post("/api/feedback", json={"course_id": 1, "question_id": 1, "rating": rating})
    assert response.status_code == 400
    assert "between 1 and 5" in response.get_json()["error"]

def test_feedback_rejects_missing_fields():
    response = client.post("/api/feedback", json={})
    assert response.status_code == 400

def test_course_rejects_empty_name():
    response = client.post("/api/courses", json={"course_name": "   "})
    assert response.status_code == 400

def test_question_rejects_empty_text():
    response = client.post("/api/questions", json={"question_text": ""})
    assert response.status_code == 400
