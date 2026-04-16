import functools
from datetime import datetime, timezone
from typing import Any, ParamSpec, TypeVar

from urllib.request import urlopen
import json

INVALID_CRITICAL_COUNT = "Breaker count must be positive integer!"
INVALID_RECOVERY_TIME = "Breaker recovery time must be positive integer!"
VALIDATIONS_FAILED = "Invalid decorator args."
TOO_MUCH = "Too much requests, just wait."

P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


class BreakerError(Exception):
    def __init__(self, func_name: str, block_time: str, message: str = TOO_MUCH):
        super().__init__(message)
        self.func_name = func_name
        self.block_time = block_time


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = 5,
        time_to_recover: int = 30,
        triggers_on: type[Exception] = Exception,
    ):
        errors = []
        if not isinstance(critical_count, int) or critical_count <= 0:
            errors.append(ValueError(INVALID_CRITICAL_COUNT))
        if not isinstance(time_to_recover, int) or time_to_recover <= 0:
            errors.append(ValueError(INVALID_RECOVERY_TIME))
        if errors:
            raise ExceptionGroup(VALIDATIONS_FAILED, errors)
        self.critical_count = critical_count
        self.time_to_recover = time_to_recover
        self.triggers_on = triggers_on

    def __call__(self, func):
        fail_count = 0
        block_time: datetime | None = None

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal fail_count, block_time

            if block_time is not None:
                now = datetime.now(timezone.utc)
                if now < block_time:
                    raise BreakerError(
                        f"{func.__module__}.{func.__name__}",
                        block_time.strftime("%Y-%m-%d %H:%M:%S"),
                    ) from None
                else:
                    fail_count = 0
                    block_time = None

            try:
                result = func(*args, **kwargs)
            except Exception as exc:
                if isinstance(exc, self.triggers_on):
                    fail_count += 1
                    if fail_count >= self.critical_count:
                        block_time = datetime.now(timezone.utc)
                        raise BreakerError(
                            f"{func.__module__}.{func.__name__}",
                            block_time.strftime("%Y-%m-%d %H:%M:%S"),
                        ) from exc
                raise
            else:
                fail_count = 0
                return result

        return wrapper


circuit_breaker = CircuitBreaker(5, 30, Exception)


def get_comments(post_id: int) -> Any:
    response = urlopen(f"https://jsonplaceholder.typicode.com/comments?postId={post_id}")
    return json.loads(response.read())


if __name__ == "__main__":
    comments = get_comments(1)
