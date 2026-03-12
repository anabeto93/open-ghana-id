from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app import app as fastapi_app


def create_app():
    return fastapi_app


@pytest.fixture(scope="session")
def client() -> TestClient:
    app = create_app()
    with TestClient(app) as c:
        yield c
