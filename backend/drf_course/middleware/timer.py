from time import perf_counter
from typing import Any

class ResponseTimerMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request, *args: Any, **kwds: Any) -> Any:
        start_time = perf_counter()

        response = self.get_response()

        res_time = perf_counter() - start_time
        print(f"API Response time to request: {res_time}")

        return response
