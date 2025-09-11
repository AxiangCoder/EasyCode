from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from .manager import UserManager

# Create your models here.
class User(AbstractUser):
    objects = UserManager()
    email = models.EmailField(
        'email',
        unique=True,
        blank=False,
        null=False,
    )
    phone = models.CharField(
        'phone',
        max_length=11,
        unique=True,
        blank=True,
        null=True,
    )

    # 声明用户模型的唯一标识符，这里我们用 email，但它可能为空
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # 让 phone 成为超级用户的必填字段

    def __str__(self):
        return self.email or self.phone or self.username

    def clean(self):
        # 自定义炎症
        if not self.email and not self.phone:
            raise ValidationError('邮箱和电话必须选填一个')
        if self.email:
            self.username = self.email
        if self.phone:
            self.phone = self.phone
        super().clean()

