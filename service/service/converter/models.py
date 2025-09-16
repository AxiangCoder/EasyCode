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
        self.sketch = load_sketch(Path (MEDIA_ROOT, 'sketches/0C46BA71-DAE4-4953-B743-9287F90A179D.json'))
        self.sketch = filter_sketch_data(self.sketch)
        with open(Path(MEDIA_ROOT, 'sketches/output.json'), "w", encoding="utf-8") as file:
            # json.dump() 函数将 Python 对象转换为 JSON 格式并写入文件
            json.dump(self.sketch, file, ensure_ascii=False, indent=4)
        print('success')
        

    
    
