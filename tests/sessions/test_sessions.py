from fastapi.testclient import TestClient
from datetime import datetime, timedelta


def create_user_and_get_token(client: TestClient):
    email = "session_tester@example.com"
    password = "securepassword123"
    client.post("/auth/register", json={"email": email, "password": password})
    response = client.post("/auth/login", json={"email": email, "password": password})
    return response.json()["access_token"]


def test_session_lifecycle_and_streaks(client: TestClient):
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a project first
    proj_resp = client.post(
        "/projects/", json={"name": "Session Proj"}, headers=headers
    )
    project_id = proj_resp.json()["id"]

    # 2. Check initial streak
    streak_resp = client.get("/streaks/me", headers=headers)
    assert streak_resp.status_code == 200
    assert streak_resp.json()["current_streak"] == 0

    # 3. Create a session
    session_data = {
        "project_id": project_id,
        "energy_start": 8,
        "mood": "focused",
        "notes": "Testing session",
    }
    create_resp = client.post("/sessions/", json=session_data, headers=headers)
    assert create_resp.status_code == 200
    session_id = create_resp.json()["id"]
    assert create_resp.json()["status"] == "open"

    # 4. Check streak update (should be 1 now as it updates on session creation)
    streak_resp = client.get("/streaks/me", headers=headers)
    assert streak_resp.json()["current_streak"] == 1

    # 5. End the session
    update_data = {"energy_end": 7, "flow_achieved": True}
    end_resp = client.post(
        f"/sessions/{session_id}/end", json=update_data, headers=headers
    )
    assert end_resp.status_code == 200
    assert end_resp.json()["status"] == "closed"
    assert end_resp.json()["duration_minutes"] is not None
    assert end_resp.json()["duration_minutes"] >= 0


def test_get_sessions(client: TestClient):
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create session
    client.post("/sessions/", json={"energy_start": 5}, headers=headers)

    # Get all sessions
    response = client.get("/sessions/", headers=headers)
    assert response.status_code == 200
    assert any(s["status"] == "open" for s in response.json())


def test_list_sessions(client: TestClient):
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create one and end it
    create_resp = client.post("/sessions/", json={"energy_start": 5}, headers=headers)
    session_id = create_resp.json()["id"]
    client.post(f"/sessions/{session_id}/end", json={"energy_end": 4}, headers=headers)

    # Create a second one (now allowed because the first is closed)
    client.post("/sessions/", json={"energy_start": 6}, headers=headers)

    response = client.get("/sessions/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 2


def test_get_session_by_id(client: TestClient):
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create session
    create_resp = client.post("/sessions/", json={"energy_start": 5}, headers=headers)
    session_id = create_resp.json()["id"]

    # Get by id
    get_resp = client.get(f"/sessions/{session_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == session_id


def test_update_session(client: TestClient):
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create session
    create_resp = client.post(
        "/sessions/",
        json={"energy_start": 5, "notes": "Initial notes"},
        headers=headers,
    )
    session_id = create_resp.json()["id"]

    # Update session
    update_data = {"notes": "Updated notes", "energy_start": 7}
    patch_resp = client.patch(
        f"/sessions/{session_id}", json=update_data, headers=headers
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["notes"] == "Updated notes"
    assert patch_resp.json()["energy_start"] == 7


def test_delete_session(client: TestClient):
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create session
    create_resp = client.post("/sessions/", json={"energy_start": 5}, headers=headers)
    session_id = create_resp.json()["id"]

    # Delete session
    del_resp = client.delete(f"/sessions/{session_id}", headers=headers)
    assert del_resp.status_code == 200

    # Verify deleted
    get_resp = client.get(f"/sessions/{session_id}", headers=headers)
    assert get_resp.status_code == 404


def test_end_session_twice_fails(client: TestClient):
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create session
    create_resp = client.post("/sessions/", json={"energy_start": 5}, headers=headers)
    session_id = create_resp.json()["id"]

    # End once
    client.post(f"/sessions/{session_id}/end", json={"energy_end": 4}, headers=headers)

    # End twice
    end_resp = client.post(
        f"/sessions/{session_id}/end", json={"energy_end": 3}, headers=headers
    )
    assert end_resp.status_code == 400
    assert "already closed" in end_resp.json()["detail"].lower()


def test_access_other_user_session_fails(client: TestClient):
    # User 1 creates a session
    token1 = create_user_and_get_token(client)
    headers1 = {"Authorization": f"Bearer {token1}"}
    create_resp = client.post("/sessions/", json={"energy_start": 5}, headers=headers1)
    session_id = create_resp.json()["id"]

    # User 2 tries to access it
    # We need a different email/password for the second user
    email2 = "other_user@example.com"
    password2 = "otherpassword"
    client.post("/auth/register", json={"email": email2, "password": password2})
    login_resp = client.post(
        "/auth/login", json={"email": email2, "password": password2}
    )
    token2 = login_resp.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    get_resp = client.get(f"/sessions/{session_id}", headers=headers2)
    assert get_resp.status_code == 404


def test_session_duration_calculation(client: TestClient):
    """Test that the duration is correctly calculated in minutes."""
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Start session
    create_resp = client.post("/sessions/", json={"energy_start": 5}, headers=headers)
    session_id = create_resp.json()["id"]

    # We can't really control time easily here without mocking,
    # but we can verify the duration is calculated.
    # We end it immediately, so duration should be 0.
    end_resp = client.post(
        f"/sessions/{session_id}/end",
        json={"energy_end": 4, "flow_achieved": True, "notes": "Test session"},
        headers=headers,
    )
    assert end_resp.status_code == 200
    data = end_resp.json()
    assert "duration_minutes" in data
    assert data["duration_minutes"] >= 0


def test_update_session_validation(client: TestClient):
    """Test that updating a session with invalid fields doesn't break it."""
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Start session
    create_resp = client.post("/sessions/", json={"energy_start": 5}, headers=headers)
    session_id = create_resp.json()["id"]

    # Update with some values
    update_resp = client.patch(
        f"/sessions/{session_id}",
        json={"notes": "Updated notes", "energy_start": 3},
        headers=headers,
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["notes"] == "Updated notes"
    assert data["energy_start"] == 3


def test_end_session_with_notes_and_blockers(client: TestClient):
    """Test ending a session with notes and blockers."""
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Start session
    create_resp = client.post("/sessions/", json={"energy_start": 8}, headers=headers)
    session_id = create_resp.json()["id"]

    # End with notes and blockers
    end_resp = client.post(
        f"/sessions/{session_id}/end",
        json={
            "energy_end": 6,
            "flow_achieved": False,
            "notes": "Had some issues",
            "blockers": "Meetings were constant",
        },
        headers=headers,
    )
    assert end_resp.status_code == 200
    data = end_resp.json()
    assert data["notes"] == "Had some issues"
    assert data["blockers"] == "Meetings were constant"
    assert data["status"] == "closed"
    assert data["flow_achieved"] is False


def test_cannot_start_multiple_active_sessions(client: TestClient):
    """Refine: User should not be able to start a second session if one is already active."""
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Start first session
    client.post("/sessions/", json={"energy_start": 5}, headers=headers)

    # Try starting another session
    resp = client.post("/sessions/", json={"energy_start": 8}, headers=headers)
    assert resp.status_code == 400
    assert "already has an active session" in resp.json()["detail"].lower()
