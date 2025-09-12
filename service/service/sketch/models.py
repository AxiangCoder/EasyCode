from django.db import models
from django.conf import settings
from core.models import BaseModel
import os


# Create your models here.
class Sketch(BaseModel):
    file_path = os.path.join('sketches/')
    file = models.FileField(upload_to=file_path)
    def __str__(self):
        return self.file.name