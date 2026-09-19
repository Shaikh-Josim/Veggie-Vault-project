import uuid
from django.db import models

from base.validators import logfile_fingerprint_validator
# base/models.py

class BaseModel(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add= True)   
    updated_at = models.DateTimeField(auto_now= True)

    class Meta:
        abstract = True

    def debug_str(self) -> str:
        return f'uid: {self.uid}, created_at: {self.created_at}, updated_at: {self.updated_at}'


class LogFile(BaseModel):
    path = models.TextField(unique=True)
    file_size = models.PositiveBigIntegerField(verbose_name= 'file size', default= 0)
    file_modified_at = models.DateTimeField(null= True, blank= True)
    file_fingerprint = models.CharField(max_length=64, blank=True, null=True, validators=[logfile_fingerprint_validator])

    def __str__(self) -> str:
        return f"logfile-path {self.path}"

    def debug_str(self) -> str:
        return f"LogFile obj: (logfile-path {self.path})"


class LogLocation(BaseModel):
    log_file = models.ForeignKey(
        LogFile,
        on_delete=models.CASCADE,
        related_name="locations",
    )
    start_position = models.PositiveBigIntegerField()
    length = models.PositiveBigIntegerField()

    def __str__(self) -> str:
        return f"start-position: {self.start_position}, length: {self.length}"

    def debug_str(self) -> str:
        return f"LogLocation obj: (start-position: {self.start_position} length: {self.length}\n log_file: |LogFile obj| {self.log_file})"


class LogIndex(BaseModel):
    location = models.ForeignKey(
        LogLocation,
        on_delete=models.CASCADE,
        related_name="indexes",
    )
    attribute_name = models.CharField(max_length=100)
    attribute_value = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["location", "attribute_name", "attribute_value"],
                name="unique_log_index_entry",
            ),
        ]
        indexes = [
            models.Index(
                fields=["attribute_name", "attribute_value"],
                name="logindex_attr_value_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"attribute_name: {self.attribute_name}, attribute_value: {self.attribute_value}"

    def debug_str(self) -> str:
        return f"LogIndex obj: (attribute_name: {self.attribute_name}, attribute_value: {self.attribute_value} \n location:|LogLocation obj| {self.location})"