"""
Smoke tests for the FastAPI application.

Tests the health endpoint and basic route presence without starting a real
server. Uses httpx.AsyncClient with the ASGI transport (no real I/O).
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient, ASGITransport


def _patch_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Provide required env vars so create_app() does not raise."""
    monkeypatch.setenv("GOOGLE_AI_API_KEY", "test-google-key")
    monkeypatch.setenv("WX_API_KEY", "test-wx-key")
    monkeypatch.setenv("WX_PROJECT_ID", "test-project")
    monkeypatch.setenv("ASTRA_DB_TOKEN", "test-astra-token")
    monkeypatch.setenv("ASTRA_DB_API_ENDPOINT", "https://test.astra.datastax.com")
    monkeypatch.setenv("ENVIRONMENT", "test")


@pytest.mark.asyncio
async def test_health_returns_200(monkeypatch: pytest.MonkeyPatch) -> None:
    """GET /health returns 200 with status=ok."""
    _patch_env(monkeypatch)

    # Reset cached settings singleton before creating the app
    import backend.core.config as cfg
    cfg._settings = None

    from backend.main import create_app
    app = create_app()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["environment"] == "test"


@pytest.mark.asyncio
async def test_diagnose_stub_returns_200(monkeypatch: pytest.MonkeyPatch) -> None:
    """POST /api/v1/diagnose returns 200 with the stub refusal_flag."""
    _patch_env(monkeypatch)

    import backend.core.config as cfg
    cfg._settings = None

    from backend.main import create_app
    app = create_app()

    payload = {
        "equipment_type": "CNC Milling Machine",
        "symptom_text": "Motor tidak bergerak setelah alarm muncul",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/diagnose", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["refusal_flag"] is True  # Stub always refuses


@pytest.mark.asyncio
async def test_report_stub_returns_200(monkeypatch: pytest.MonkeyPatch) -> None:
    """POST /api/v1/report/{uuid} returns 200 with placeholder markdown."""
    _patch_env(monkeypatch)

    import backend.core.config as cfg
    cfg._settings = None

    from backend.main import create_app
    app = create_app()

    test_uuid = "00000000-0000-0000-0000-000000000001"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(f"/api/v1/report/{test_uuid}")

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == test_uuid
    assert "markdown" in data


@pytest.mark.asyncio
async def test_report_invalid_uuid_returns_422(monkeypatch: pytest.MonkeyPatch) -> None:
    """POST /api/v1/report/not-a-uuid returns 422 Unprocessable Entity."""
    _patch_env(monkeypatch)

    import backend.core.config as cfg
    cfg._settings = None

    from backend.main import create_app
    app = create_app()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/report/not-a-valid-uuid")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_diagnose_rejects_short_symptom(monkeypatch: pytest.MonkeyPatch) -> None:
    """POST /api/v1/diagnose rejects symptom_text shorter than 5 chars."""
    _patch_env(monkeypatch)

    import backend.core.config as cfg
    cfg._settings = None

    from backend.main import create_app
    app = create_app()

    payload = {
        "equipment_type": "CNC",
        "symptom_text": "hi",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/diagnose", json=payload)

    assert response.status_code == 422
