from django.db import models
import uuid

# Create your models here.
class Converter(models.Model):
    project_name = models.CharField(max_length=100)
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)