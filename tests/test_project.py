import ast
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_app_syntax():
    ast.parse((ROOT/"app.py").read_text(encoding="utf-8"))

def test_schema_constraints():
    sql=(ROOT/"database/schema.sql").read_text(encoding="utf-8")
    assert "CHECK (rating BETWEEN 1 AND 5)" in sql
    assert "FOREIGN KEY (course_id)" in sql
    assert "FOREIGN KEY (question_id)" in sql

def test_templates_exist():
    assert (ROOT/"templates/index.html").exists()
    assert (ROOT/"templates/dashboard.html").exists()

def test_env_not_committed():
    assert not (ROOT/".env").exists()
