from django.db import models
import uuid
from .sketch_parser import load_sketch, filter_sketch_data
from service.settings import MEDIA_ROOT
from pathlib import Path
import json
# Create your models here.
class Converter(models.Model):
    project_name = models.CharField(max_length=100)
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    def __init__(self):
        self.sketch = load_sketch(Path (MEDIA_ROOT, 'sketches/4592D46D-EB87-4A2A-B792-6DB3FFCD2AA4.json'))
        self.sketch = filter_sketch_data(self.sketch)
        print(json.dumps(self.sketch))
        

    
    
