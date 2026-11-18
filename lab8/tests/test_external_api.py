import asyncio

import httpx
import pytest

from employee_manager.external_api import (
    fetch_department_statistics,
    fetch_departments_statistics,
)


def make_client(handler) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://test")


@pytest.mark.asyncio
async def test_gather_returns_results_in_order() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        department_id = int(request.url.path.split("/")[2])
        return httpx.Response(200, json={"department_id": department_id})

    async with make_client(handler) as client:
        results = await fetch_departments_statistics(client, [3, 1, 2])

    assert [item["department_id"] for item in results] == [3, 1, 2]


@pytest.mark.asyncio
async def test_semaphore_limits_parallel_requests() -> None:
    active = 0
    max_active = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal active, max_active
        active += 1
        max_active = max(max_active, active)
        await asyncio.sleep(0.05)
        active -= 1
        return httpx.Response(200, json={})

    async with make_client(handler) as client:
        await fetch_departments_statistics(client, list(range(1, 11)), limit=3)

    assert max_active == 3


@pytest.mark.asyncio
async def test_retry_after_server_errors() -> None:
    calls = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls < 3:
            return httpx.Response(503)
        return httpx.Response(200, json={"department_id": 1})

    async with make_client(handler) as client:
        result = await fetch_department_statistics(client, asyncio.Semaphore(1), 1, delay=0)

    assert result == {"department_id": 1}
    assert calls == 3


@pytest.mark.asyncio
async def test_retry_gives_up_after_attempts() -> None:
    calls = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise httpx.ConnectError("Connection refused", request=request)

    async with make_client(handler) as client:
        with pytest.raises(httpx.ConnectError):
            await fetch_department_statistics(client, asyncio.Semaphore(1), 1, delay=0)

    assert calls == 3


@pytest.mark.asyncio
async def test_no_retry_for_404() -> None:
    calls = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(404, json={"detail": "Department not found"})

    async with make_client(handler) as client:
        with pytest.raises(httpx.HTTPStatusError):
            await fetch_department_statistics(client, asyncio.Semaphore(1), 99, delay=0)

    assert calls == 1


@pytest.mark.asyncio
async def test_timeout() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        await asyncio.sleep(1)
        return httpx.Response(200, json={})

    async with make_client(handler) as client:
        with pytest.raises(TimeoutError):
            await asyncio.wait_for(fetch_departments_statistics(client, [1, 2]), timeout=0.1)