def test_register_creates_parent_and_returns_tokens(client):
    res = client.post(
        "/api/v1/auth/register",
        json={"name": "Alice", "email": "alice@test.com", "password": "Passw0rd!"},
    )
    assert res.status_code == 201
    data = res.get_json()["data"]
    assert data["user"]["role"] == "PARENT"
    assert "accessToken" in data and "refreshToken" in data
    assert "password" not in data["user"] and "passwordHash" not in data["user"]


def test_register_duplicate_email_rejected(client):
    payload = {"name": "Bob", "email": "bob@test.com", "password": "Passw0rd!"}
    first = client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201
    second = client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409
    assert second.get_json()["error"]["code"] == "EMAIL_TAKEN"


def test_login_with_wrong_password_rejected(client, registered_parent):
    res = client.post(
        "/api/v1/auth/login", json={"email": registered_parent["email"], "password": "WrongPassword!"}
    )
    assert res.status_code == 401
    assert res.get_json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_protected_endpoint_requires_token(client):
    res = client.get("/api/v1/parents/me")
    assert res.status_code == 401


def test_protected_endpoint_rejects_garbage_token(client):
    res = client.get("/api/v1/parents/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert res.status_code == 401
    assert res.get_json()["error"]["code"] == "TOKEN_INVALID"


def test_refresh_rotates_tokens(client, registered_parent):
    res = client.post("/api/v1/auth/refresh", json={"refreshToken": registered_parent["refreshToken"]})
    assert res.status_code == 200
    new_tokens = res.get_json()["data"]
    assert new_tokens["accessToken"] != registered_parent["accessToken"]

    # The old refresh token was rotated out — reusing it must fail.
    reuse = client.post("/api/v1/auth/refresh", json={"refreshToken": registered_parent["refreshToken"]})
    assert reuse.status_code == 401


def test_child_login_with_correct_pin(client, registered_parent, child):
    res = client.post(
        "/api/v1/auth/child-login",
        json={"studentId": child["id"], "pin": "1234"},
        headers=registered_parent["headers"],
    )
    assert res.status_code == 200
    assert "accessToken" in res.get_json()["data"]


def test_child_login_with_wrong_pin_rejected(client, registered_parent, child):
    res = client.post(
        "/api/v1/auth/child-login",
        json={"studentId": child["id"], "pin": "9999"},
        headers=registered_parent["headers"],
    )
    assert res.status_code == 401
    assert res.get_json()["error"]["code"] == "INVALID_PIN"


def test_parent_cannot_child_login_as_someone_elses_child(client, registered_parent):
    # A second parent's child should not be reachable from the first parent's token.
    other = client.post(
        "/api/v1/auth/register",
        json={"name": "Other Parent", "email": "other@test.com", "password": "Passw0rd!"},
    ).get_json()["data"]
    other_child = client.post(
        "/api/v1/parents/me/children",
        json={"name": "Other Kid", "classGrade": "Class 8", "targetBoard": "CBSE", "pin": "1111"},
        headers={"Authorization": f"Bearer {other['accessToken']}"},
    ).get_json()["data"]

    res = client.post(
        "/api/v1/auth/child-login",
        json={"studentId": other_child["id"], "pin": "1111"},
        headers=registered_parent["headers"],
    )
    assert res.status_code == 404
