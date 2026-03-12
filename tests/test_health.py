from __future__ import annotations


def test_health(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "Welcome to the Open Ghana ID" in body["message"]
