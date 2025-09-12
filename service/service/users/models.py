from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
import uuid
from core.models import CustomUserManager, BaseModel


# Create your models here.


class User(AbstractUser, BaseModel):
    email = models.EmailField(unique=True, null=False, blank=False)
    avatar = models.URLField(blank=True)
    role = models.CharField(max_length=10, default='admin')
    username = None
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # email 已经作为 USERNAME_FIELD，不需要在 REQUIRED_FIELDS 中
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        ordering = ['-date_joined']
    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
