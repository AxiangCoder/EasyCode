import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

# Create your models here.

class CustomUserManager(UserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user



class BaseModel(models.Model):
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_delete=models.BooleanField(default=False)
    # 关联到创建人
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # 引用自定义的用户模型
        on_delete=models.PROTECT,  # 用户被删除时，其创建的产品也一并删除
        related_name='sketches',   # 反向关联名，可以通过 user.sketches 获取该用户创建的所有产品
        null=True, blank=True
    )

