from __future__ import annotations

from httpx import AsyncClient


async def test_health_check(client: AsyncClient) -> None:
    """Health endpoint returns 200 with status ok."""
    response = await client.get("/api/v1/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
