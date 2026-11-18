import logging
from collections.abc import Iterator
from contextlib import contextmanager
from time import perf_counter

logger = logging.getLogger(__name__)


@contextmanager
def logged_operation(operation: str) -> Iterator[None]:
    logger.info("%s started", operation)
    start = perf_counter()

    try:
        yield
    except Exception:
        logger.exception("%s failed", operation)
        raise
    else:
        elapsed = perf_counter() - start
        logger.info("%s finished in %.6f s", operation, elapsed)