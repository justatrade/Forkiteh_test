from fastapi.testclient import TestClient

from main import app


client = TestClient(app)

def test_post_wallet_info():
    wallet_address = "TUjAV9HUw6w7TN7w8bhkmkKxjqGY8x3u2V"
    response = client.post("/wallet_info", json={"address": wallet_address})
    assert response.status_code == 200
    assert "bandwidth" in response.json()
    assert "energy" in response.json()
    assert "trx_balance" in response.json()

def test_get_wallet_queries():
    response = client.get("/wallet_queries?skip=0&limit=5")
    assert response.status_code == 200
    assert isinstance(response.json(), list)