def test_create_todo(client, auth_headers):
    resp = client.post("/api/v1/todos/", json={"title": "운동하기", "description": "30분 달리기"}, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "운동하기"
    assert data["is_completed"] is False
    assert "user_id" not in data


def test_create_todo_without_description(client, auth_headers):
    resp = client.post("/api/v1/todos/", json={"title": "물 마시기"}, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["description"] is None


def test_list_todos(client, auth_headers):
    client.post("/api/v1/todos/", json={"title": "A"}, headers=auth_headers)
    client.post("/api/v1/todos/", json={"title": "B"}, headers=auth_headers)
    resp = client.get("/api/v1/todos/", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_list_todos_only_own(client, auth_headers):
    client.post("/api/v1/todos/", json={"title": "내 할 일"}, headers=auth_headers)

    client.post("/api/v1/users/register", json={"email": "other@example.com", "password": "password123"})
    other_login = client.post(
        "/api/v1/users/login", data={"email": "other@example.com", "password": "password123"}
    )
    other_headers = {"Authorization": f"Bearer {other_login.json()['access_token']}"}
    client.post("/api/v1/todos/", json={"title": "남의 할 일"}, headers=other_headers)

    resp = client.get("/api/v1/todos/", headers=auth_headers)
    assert len(resp.json()) == 1


def test_update_todo_title(client, auth_headers):
    todo_id = client.post("/api/v1/todos/", json={"title": "원래 제목"}, headers=auth_headers).json()["id"]
    resp = client.patch(f"/api/v1/todos/{todo_id}", json={"title": "수정된 제목"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "수정된 제목"


def test_complete_todo(client, auth_headers):
    todo_id = client.post("/api/v1/todos/", json={"title": "완료할 항목"}, headers=auth_headers).json()["id"]
    resp = client.patch(f"/api/v1/todos/{todo_id}", json={"is_completed": True}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["is_completed"] is True


def test_update_other_user_todo_returns_404(client, auth_headers):
    client.post("/api/v1/users/register", json={"email": "other@example.com", "password": "password123"})
    other_login = client.post(
        "/api/v1/users/login", data={"email": "other@example.com", "password": "password123"}
    )
    other_headers = {"Authorization": f"Bearer {other_login.json()['access_token']}"}
    todo_id = client.post("/api/v1/todos/", json={"title": "남의 할 일"}, headers=other_headers).json()["id"]

    resp = client.patch(f"/api/v1/todos/{todo_id}", json={"title": "해킹 시도"}, headers=auth_headers)
    assert resp.status_code == 404


def test_delete_todo(client, auth_headers):
    todo_id = client.post("/api/v1/todos/", json={"title": "삭제할 항목"}, headers=auth_headers).json()["id"]
    resp = client.delete(f"/api/v1/todos/{todo_id}", headers=auth_headers)
    assert resp.status_code == 204

    resp = client.get("/api/v1/todos/", headers=auth_headers)
    assert len(resp.json()) == 0


def test_delete_other_user_todo_returns_404(client, auth_headers):
    client.post("/api/v1/users/register", json={"email": "other@example.com", "password": "password123"})
    other_login = client.post(
        "/api/v1/users/login", data={"email": "other@example.com", "password": "password123"}
    )
    other_headers = {"Authorization": f"Bearer {other_login.json()['access_token']}"}
    todo_id = client.post("/api/v1/todos/", json={"title": "남의 할 일"}, headers=other_headers).json()["id"]

    resp = client.delete(f"/api/v1/todos/{todo_id}", headers=auth_headers)
    assert resp.status_code == 404
