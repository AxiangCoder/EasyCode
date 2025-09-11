from django.contrib.auth.models import UserManager as BaseUserManager
# from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError



class UserManager(BaseUserManager):
    def create_user(self, email=None , phone=None, password=None, **extra_fields):
        if not email and not phone:
            raise ValidationError('邮箱和电话号码必须填写一个。')
        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email=None , phone=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, phone, password, **extra_fields)