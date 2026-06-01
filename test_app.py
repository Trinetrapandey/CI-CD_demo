"""
Automated tests.
The CI stage of our pipeline runs these. If ANY test fails,
the pipeline stops and the broken code is NEVER deployed.
This is the safety net that makes automation trustworthy.
"""
from app import app, add


def test_home_page_works():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert response.json["status"] == "running"


def test_health_check_works():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_add_function():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
