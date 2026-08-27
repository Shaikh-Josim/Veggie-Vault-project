import uuid
from django.db import models

# base/models.py

class BaseModel(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add= True)
    updated_at = models.DateTimeField(auto_now= True)

    class Meta:
        abstract = True

    def debug_str(self) -> str:
        return f'uid: {self.uid}, created_at: {self.created_at}, updated_at: {self.updated_at}'
