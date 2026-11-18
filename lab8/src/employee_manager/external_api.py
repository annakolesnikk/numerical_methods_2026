import asyncio
import time
from typing import Any

import httpx

from employee_manager.dependencies import API_BASE_URL


async def fetch_department_statistics(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    department_id: int,
    attempts: int = 3,
    delay: float = 0.5,
) -> dict[str, Any]:
    async with semaphore:
        for attempt in range(1, attempts + 1):
            try:
                response = await client.get(f"/departments/{department_id}/statistics")
                response.raise_for_status()
                result: dict[str, Any] = response.json()
                return result
            except httpx.HTTPStatusError as error:
                # 4xx is a client error: retrying will not help.
                if error.response.status_code < 500 or attempt == attempts:
                    raise
            except httpx.RequestError:
                if attempt == attempts:
                    raise
            await asyncio.sleep(delay * attempt)  # backoff: 0.5 s, 1 s, ...

    raise RuntimeError("Unexpected retry state")


async def fetch_departments_statistics(
    client: httpx.AsyncClient,
    department_ids: list[int],
    limit: int = 3,
    delay: float = 0.5,
) -> list[dict[str, Any]]:
    semaphore = asyncio.Semaphore(limit)
    tasks = [
        asyncio.create_task(
            fetch_department_statistics(client, semaphore, department_id, delay=delay)
        )
        for department_id in department_ids
    ]
    return list(await asyncio.gather(*tasks))


async def main() -> None:
    start = time.perf_counter()
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=5.0) as client:
        try:
            results = await asyncio.wait_for(
                fetch_departments_statistics(client, [1, 2, 3]),
                timeout=10.0,
            )
        except TimeoutError:
            print("Timeout: statistics were not received in 10 s")
            return

    for item in results:
        print(item)
    print(f"Received {len(results)} departments in {time.perf_counter() - start:.3f} s")


if __name__ == "__main__":
    asyncio.run(main())