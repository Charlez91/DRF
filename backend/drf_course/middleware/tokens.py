
from typing import Any


class TokenMiddleware:

    def __init__(self, get_response) -> None:
        self.get_response = get_response
    
    def __call__(self, request, *args: Any, **kwds: Any) -> Any:
        token = request.COOKIES.get("access_token")
        auth_header = request.META.get("HTTP_AUTHORIZATION")

        if auth_header is not None and "Token" in auth_header:
            response = self.get_response(request)
            return response
        
        if token:
            request.META["HTTP_AUTHORIZATION"] = f"Token {token}"
        
        response = self.get_response(request)
        return response
