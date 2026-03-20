import functools
import time
from collections import deque


class NotAliveError(Exception):
    pass


def circuit_breaker(
    state_count: int,
    error_count: int,
    network_errors: list[type[Exception]],
    sleep_time_sec: int,
):
    if state_count <= 10:
        raise ValueError("state_count должен быть > 10")
    if error_count >= 10:
        raise ValueError("error_count должен быть < 10")

    def decorator(func):
        buffer = deque(maxlen=state_count)
        allowed_errors = tuple(network_errors)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if len(buffer) >= error_count and all(item is False for item in list(buffer)[-error_count:]):
                raise NotAliveError()
            if buffer and buffer[-1] is False:
                time.sleep(sleep_time_sec)
            try:
                result = func(*args, **kwargs)
                buffer.append(True)
                return result
            except allowed_errors:
                buffer.append(False)
                raise
            except Exception:
                raise

        return wrapper

    return decorator
