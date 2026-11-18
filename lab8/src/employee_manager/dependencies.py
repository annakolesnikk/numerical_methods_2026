import os
from collections.abc import AsyncIterator, Iterator

import httpx
from sqlalchemy.orm import Session

from employee_manager.database import SessionLocal

API_BASE_URL = os.getenv("EMPLOYEE_API_URL", "http://127.0.0.1:8000")


def get_session() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


async def get_http_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=5.0) as client:
        yield client