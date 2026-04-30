def test_register_success(client):
    resp = client.post("/api/v1/users/register", json={"email": "new@example.com", "password": "password123"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "new@example.com"
    assert data["is_active"] is True
    assert "id" in data


def test_register_duplicate_email(client):
    payload = {"email": "dup@example.com", "password": "password123"}
    client.post("/api/v1/users/register", json=payload)
    resp = client.post("/api/v1/users/register", json=payload)
    assert resp.status_code == 400


def test_register_short_password(client):
    resp = client.post("/api/v1/users/register", json={"email": "x@example.com", "password": "short"})
    assert resp.status_code == 422


def test_login_success(client, registered_user):
    resp = client.post(
        "/api/v1/users/login",
        data={"email": registered_user["email"], "password": registered_user["password"]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, registered_user):
    resp = client.post(
        "/api/v1/users/login",
        data={"email": registered_user["email"], "password": "wrongpassword"},
    )
    assert resp.status_code == 401


def test_login_unknown_email(client):
    resp = client.post(
        "/api/v1/users/login",
        data={"email": "nobody@example.com", "password": "password123"},
    )
    assert resp.status_code == 401


def test_protected_endpoint_without_token(client):
    resp = client.get("/api/v1/todos/")
    assert resp.status_code == 401
