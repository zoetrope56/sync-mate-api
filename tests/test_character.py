def test_create_character(client, auth_headers):
    resp = client.post("/api/v1/character/", json={"name": "모찌"}, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "모찌"
    assert data["level"] == 1
    assert data["exp"] == 0
    assert "user_id" not in data


def test_create_duplicate_character(client, auth_headers):
    client.post("/api/v1/character/", json={"name": "모찌"}, headers=auth_headers)
    resp = client.post("/api/v1/character/", json={"name": "모찌2"}, headers=auth_headers)
    assert resp.status_code == 400


def test_get_character(client, auth_headers):
    client.post("/api/v1/character/", json={"name": "모찌"}, headers=auth_headers)
    resp = client.get("/api/v1/character/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "모찌"


def test_get_character_not_found(client, auth_headers):
    resp = client.get("/api/v1/character/", headers=auth_headers)
    assert resp.status_code == 404


def test_interact_increases_happiness_and_exp(client, auth_headers):
    client.post("/api/v1/character/", json={"name": "모찌"}, headers=auth_headers)
    before = client.get("/api/v1/character/", headers=auth_headers).json()

    resp = client.post("/api/v1/character/interact", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["character"]["happiness"] > before["happiness"]
    assert data["character"]["exp"] > before["exp"]
    assert "leveled_up" in data
    assert data["message"] == "캐릭터를 쓰다듬었습니다!"


def test_interact_without_character(client, auth_headers):
    resp = client.post("/api/v1/character/interact", headers=auth_headers)
    assert resp.status_code == 404


def test_todo_complete_increases_character_exp(client, auth_headers):
    client.post("/api/v1/character/", json={"name": "모찌"}, headers=auth_headers)
    before = client.get("/api/v1/character/", headers=auth_headers).json()

    todo_id = client.post("/api/v1/todos/", json={"title": "운동"}, headers=auth_headers).json()["id"]
    client.patch(f"/api/v1/todos/{todo_id}", json={"is_completed": True}, headers=auth_headers)

    after = client.get("/api/v1/character/", headers=auth_headers).json()
    assert after["exp"] > before["exp"]
    assert after["happiness"] > before["happiness"]


def test_levelup_on_interact(client, auth_headers):
    from app.services.character_logic import INTERACT_EXP, EXP_PER_LEVEL

    client.post("/api/v1/character/", json={"name": "모찌"}, headers=auth_headers)

    interactions_needed = EXP_PER_LEVEL // INTERACT_EXP
    leveled_up = False
    for _ in range(interactions_needed + 1):
        resp = client.post("/api/v1/character/interact", headers=auth_headers)
        if resp.json()["leveled_up"]:
            leveled_up = True
            break

    assert leveled_up
    char = client.get("/api/v1/character/", headers=auth_headers).json()
    assert char["level"] == 2
