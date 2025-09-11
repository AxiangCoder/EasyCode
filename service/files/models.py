from django.db import models
from django.conf import settings # 导入 settings

# Create your models here.

class File(models.Model):
    file = models.FileField(upload_to='files')
    createTime = models.DateTimeField(auto_now_add=True)
    updateTime = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    def __str__(self):
        return self.file.name