from django.db import models
from django.conf import settings

# Create your models here.
class Sketch(models.Model):
    file = models.FileField(upload_to='upload/sketches/')
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    id=models.AutoField(primary_key=True)
    is_delete=models.BooleanField(default=False)
    # 关联到创建人
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # 引用自定义的用户模型
        on_delete=models.CASCADE,  # 用户被删除时，其创建的产品也一并删除
        related_name='sketches',   # 反向关联名，可以通过 user.sketches 获取该用户创建的所有产品
    )

    def __str__(self):
        return self.file.name