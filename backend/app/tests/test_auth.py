def test_register_and_login(client):
    # 1. Register new user
    res = client.post(
        "/api/v1/auth/register",
        json={
            "email": "candidate@example.com",
            "password": "SecretPassword123!",
            "full_name": "Test Candidate"
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "candidate@example.com"
    token = data["access_token"]

    # 2. Access /auth/me with Bearer token
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "candidate@example.com"

    # 3. Unauthenticated access blocked
    unauth_res = client.get("/api/v1/auth/me")
    assert unauth_res.status_code == 401

    # 4. Login with registered credentials
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "email": "candidate@example.com",
            "password": "SecretPassword123!"
        }
    )
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()
