from django.db import models
from django.conf import settings
import uuid
from core.models import BaseModel


# Create your models here.
class Sketch(BaseModel):
    file = models.FileField(upload_to='upload/sketches/')
    def __str__(self):
        return self.file.name