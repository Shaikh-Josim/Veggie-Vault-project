import uuid
from typing import cast, Callable

from contextvars import ContextVar
from collections.abc import Callable
from django.http import HttpRequest, HttpResponse



request_id = ContextVar("request_id", default="-")


class RequestIDMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self,  request: HttpRequest) -> HttpResponse:
        token = request_id.set(str(uuid.uuid4()))

        try:
            return self.get_response(request)
        finally:
            request_id.reset(token)


