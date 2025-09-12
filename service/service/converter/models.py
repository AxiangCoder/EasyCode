from django.db import models
import uuid
from .sketch_parser import load_sketch
from service.settings import MEDIA_ROOT
from pathlib import Path
# Create your models here.
class Converter(models.Model):
    project_name = models.CharField(max_length=100)
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    def __init__(self):
        self.sketch = load_sketch(Path (MEDIA_ROOT, 'sketches/555EAECD-44FD-4422-8BAE-E20B3334130D.json'))
        print(self.sketch)
        

    
    
