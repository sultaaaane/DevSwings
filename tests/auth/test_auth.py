from fastapi.testclient import TestClient


def test_register_user(client: TestClient):
    response = client.post(
        "/auth/register",
        json={"email": "tester@example.com", "password": "securepassword123"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Account created successfully"


def test_login_user(client: TestClient):
    # Register first
    client.post(
        "/auth/register",
        json={"email": "login@example.com", "password": "loginpassword"},
    )
    # Login
    response = client.post(
        "/auth/login", json={"email": "login@example.com", "password": "loginpassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


def test_duplicate_register(client: TestClient):
    client.post(
        "/auth/register",
        json={"email": "dup@example.com", "password": "securepassword"},
    )
    response = client.post(
        "/auth/register",
        json={"email": "dup@example.com", "password": "securepassword"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"
