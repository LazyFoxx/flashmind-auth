from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_refresh_cookie():
    # Сначала логин
    login_resp = client.post(
        "/api/v1/auth/login", json={"email": "...", "password": "..."}
    )
    assert login_resp.status_code == 200
    cookies = login_resp.cookies  # FastAPI TestClient сохраняет куки

    # Refresh
    refresh_resp = client.post("/api/v1/auth/refresh", cookies=cookies)
    assert refresh_resp.status_code == 200
    data = refresh_resp.json()
    assert data["refresh_token"] is None
    assert "access_token" in data

    # Проверяем, что кука обновилась
    new_cookie = refresh_resp.cookies["refresh_token"]
    assert new_cookie != cookies["refresh_token"]  # ← главный assert!
