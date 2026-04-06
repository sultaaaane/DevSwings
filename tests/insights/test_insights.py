import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

def create_user_and_get_token(client: TestClient):
    email = f"insights_tester_{uuid4()}@example.com"
    password = "securepassword123"
    client.post("/auth/register", json={"email": email, "password": password})
    response = client.post("/auth/login", json={"email": email, "password": password})
    return response.json()["access_token"]


def test_get_user_stats_empty(client: TestClient):
    """Test retrieving stats for a user with no sessions or commits."""
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/insights/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_sessions"] == 0
    assert data["total_commits"] == 0
    assert data["average_energy_start"] is None

def test_get_user_stats_with_data(client: TestClient):
    """Test retrieving stats after creating sessions."""
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create and end a session
    s1 = client.post("/sessions/", json={"energy_start": 8}, headers=headers).json()
    client.post(f"/sessions/{s1['id']}/end", json={"energy_end": 6, "flow_achieved": True}, headers=headers)
    
    # 2. Create another session but leave it open
    client.post("/sessions/", json={"energy_start": 4}, headers=headers)
    
    response = client.get("/insights/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_sessions"] == 2
    assert data["flow_sessions_count"] == 1
    # energy start avg: (8 + 4) / 2 = 6.0
    assert data["average_energy_start"] == 6.0
    # energy end avg: (6) / 1 = 6.0
    assert data["average_energy_end"] == 6.0

def test_list_insights_empty(client: TestClient):
    """Test listing generated insights (e.g. periodically computed ones)."""
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/insights/history", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_stats_with_invalid_project_id(client: TestClient):
    """Test that passing a non-existent project_id returns 0 stats (or filters correctly)."""
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    fake_id = str(uuid4())
    response = client.get(f"/insights/me?project_id={fake_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_sessions"] == 0
