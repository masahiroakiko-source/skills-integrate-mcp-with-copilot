from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


def reset_activity(activity_name="Chess Club"):
    activities[activity_name]["participants"] = [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def login():
    response = client.post("/login", params={
        "username": "teacher",
        "password": "admin",
    })
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['token']}"}


def test_students_can_view_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    assert "Chess Club" in response.json()


def test_signup_requires_teacher_login():
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "student@mergington.edu"},
    )
    assert response.status_code == 401
    assert "authentication required" in response.json()["detail"].lower()


def test_unregister_requires_teacher_login():
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "michael@mergington.edu"},
    )
    assert response.status_code == 401
    assert "authentication required" in response.json()["detail"].lower()


def test_teacher_can_register_and_unregister_student():
    reset_activity()
    headers = login()

    signup = client.post(
        "/activities/Chess Club/signup",
        params={"email": "student@mergington.edu"},
        headers=headers,
    )
    assert signup.status_code == 200
    assert "student@mergington.edu" in activities["Chess Club"]["participants"]

    unregister = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "student@mergington.edu"},
        headers=headers,
    )
    assert unregister.status_code == 200
    assert "student@mergington.edu" not in activities["Chess Club"]["participants"]


def test_invalid_credentials_are_rejected():
    response = client.post("/login", params={
        "username": "teacher",
        "password": "wrong",
    })
    assert response.status_code == 401
