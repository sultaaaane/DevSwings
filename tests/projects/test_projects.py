from uuid import UUID
from fastapi.testclient import TestClient


def create_user_and_get_token(client: TestClient):
    email = "project_tester@example.com"
    password = "securepassword123"
    client.post("/auth/register", json={"email": email, "password": password})
    response = client.post("/auth/login", json={"email": email, "password": password})
    return response.json()["access_token"]


def test_create_project(client: TestClient):
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    project_data = {
        "name": "Test Project",
        "description": "A project for testing",
        "color": "#FF0000",
        "weekly_goal_hours": 10.0,
        "github_repo": "owner/repo",
    }

    response = client.post("/projects/", json=project_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert "id" in data
    return data["id"]


def test_get_projects(client: TestClient):
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create two projects
    client.post("/projects/", json={"name": "Project 1"}, headers=headers)
    client.post("/projects/", json={"name": "Project 2"}, headers=headers)

    response = client.get("/projects/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Filter by user in database means we might see other projects if database not reset,
    # but conftest normally provides a clean DB per session or function depending on setup.
    # Assuming clean DB here.
    assert len(data) >= 2


def test_update_project(client: TestClient):
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create
    create_resp = client.post("/projects/", json={"name": "Old Name"}, headers=headers)
    project_id = create_resp.json()["id"]

    # Update
    update_data = {"name": "New Name", "status": "completed"}
    response = client.patch(
        f"/projects/{project_id}", json=update_data, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"
    assert response.json()["status"] == "completed"


def test_delete_project(client: TestClient):
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create
    create_resp = client.post("/projects/", json={"name": "To Delete"}, headers=headers)
    project_id = create_resp.json()["id"]

    # Delete
    response = client.delete(f"/projects/{project_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Project deleted successfully"

    # Verify 404
    get_resp = client.get(f"/projects/{project_id}", headers=headers)
    # The router might not have a GET /{id} endpoint, but let's check the list
    list_resp = client.get("/projects/", headers=headers)
    project_ids = [p["id"] for p in list_resp.json()]
    assert project_id not in project_ids


def test_cannot_access_other_user_project(client: TestClient):
    """Test that projects are private and cannot be deleted by another user."""
    # User 1 creates a project
    token1 = create_user_and_get_token(client)
    headers1 = {"Authorization": f"Bearer {token1}"}
    create_resp1 = client.post("/projects/", json={"name": "User 1 Project"}, headers=headers1)
    p1_id = create_resp1.json()["id"]

    # User 2 tries to delete it
    from uuid import uuid4
    email2 = f"user2_{uuid4()}@example.com"
    client.post("/auth/register", json={"email": email2, "password": "password123"})
    token2 = client.post("/auth/login", json={"email": email2, "password": "password123"}).json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    del_resp = client.delete(f"/projects/{p1_id}", headers=headers2)
    assert del_resp.status_code == 404 # Or 403, but service usually raises ValueError("Project not found")


def test_update_project_goal(client: TestClient):
    """Test updating only the weekly goal of a project."""
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    create_resp = client.post("/projects/", json={"name": "Goal Project", "weekly_goal_hours": 5}, headers=headers)
    p_id = create_resp.json()["id"]
    
    update_resp = client.patch(f"/projects/{p_id}", json={"weekly_goal_hours": 20}, headers=headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["weekly_goal_hours"] == 20
