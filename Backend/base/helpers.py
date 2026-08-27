from typing import Any, Dict, cast, Union
from functools import wraps
from django.utils import timezone
from datetime import timedelta
from celery import Task
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status
from rest_framework.serializers import Serializer, ListSerializer
from base.exceptions import *

def validated_dict(serializer: Union[Serializer, ListSerializer]) -> Dict[str, Any]:
    """
    Run is_valid(raise_exception=True) and return validated_data
    as a typed dict for Pylance/mypy.
    """
    serializer.is_valid(raise_exception=True)
    return cast(Dict[str, Any], serializer.validated_data)

def pop_update_dict_data(data: dict, remove_keys:None|list = None, overrides:None|dict = None):
    remove_keys = remove_keys or []
    overrides = overrides or {}
    return {
        **{k: v for k, v in data.items() if k not in remove_keys},
        **overrides
    }




def require_idempotency_key(timeout=10):
    """
    Decorator factory enforcing a frontend-provided X-Idempotency-Key header.
    Blocks concurrent identical requests and clears locks cleanly upon completion.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # 1. Fetch the idempotency key from the frontend
            frontend_uuid = request.META.get('HTTP_X_IDEMPOTENCY_KEY')

            # 2. Stop Process and Return Response if no key
            if not frontend_uuid:
                return Response(
                    {"error": "Secure operations require an 'X-Idempotency-Key' header."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 3. Create a unique Redis lock key tied to the user and their specific UUID
            user_id = request.user.uid if request.user.is_authenticated else "anonymous"
            redis_key = f"idempotency_{user_id}_{frontend_uuid}"

            # 4. Atomically check/add the lock key in Redis
            is_new_request = cache.add(redis_key, "processing", timeout=timeout)

            if not is_new_request:
                return Response(
                    {"error": "Your request is already being processed. Please wait."},
                    status=status.HTTP_409_CONFLICT
                )

            # 5. Run the view logic 
            try:
                response = view_func(request, *args, **kwargs)
                return response
            finally:
                # 6. Crucial Cleanup: Wipe the lock from Redis when the view is done
                cache.delete(redis_key)
                
        return wrapper
    return decorator

def schedule_task(function:Task, days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0, **kwargs):
    print("Entering in schedule_task helper..")
    if not any([days, seconds, microseconds, milliseconds, minutes, hours, weeks]):
        raise NotFound("time need to be specified for scheduling task")

    run_time = timezone.now() + timedelta(days, seconds, microseconds, milliseconds, minutes, hours, weeks)
    
    function.apply_async(eta=run_time, kwargs = kwargs)
    print("leaving from schedule_task helper..")
