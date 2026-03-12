from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient


def test_validate_ghana_card_number(client: TestClient):
    with patch("routers.ghana_card_number.validate_ghana_card_number", return_value=True):
        response = client.post(
            "/validate-ghana-card-number",
            json={"card_num": "GHA-000000000-0"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_validate_tin(client: TestClient):
    with patch("routers.tin.validate_tin", return_value=True):
        response = client.post(
            "/validate-tin",
            json={"tin_num": "P0000000000"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
