import uuid
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class RequestIDMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Generate a unique ID for each incoming request
        request.id = str(uuid.uuid4())

    def process_response(self, request, response):
        # Attach request ID to response headers for debugging
        if hasattr(request, "id"):
            response["X-Request-ID"] = request.id
        return response
