from typing import Any, Dict, cast, Union
from rest_framework.serializers import Serializer, ListSerializer

def validated_dict(serializer: Union[Serializer, ListSerializer]) -> Dict[str, Any]:
    """
    Run is_valid(raise_exception=True) and return validated_data
    as a typed dict for Pylance/mypy.
    """
    serializer.is_valid(raise_exception=True)
    return cast(Dict[str, Any], serializer.validated_data)
