from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings

class UserManager(BaseUserManager):
    """
    Кастомный менеджер пользователей, работающий с email как с уникальным идентификатором.
    Используется моделью :model:`users.User`.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Создаёт и сохраняет обычного пользователя с указанным email и паролем.
        """
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Создаёт и сохраняет суперпользователя.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Кастомная модель пользователя.

    **Поля**
    * ``email`` — уникальный email, используется для входа.
    * ``phone`` — номер телефона (необязательно).
    * ``city`` — город проживания.
    * ``avatar`` — аватар пользователя.

    Связанные модели:
    * :model:`users.Payment`
    * :model:`materials.Course` (через поле `owner`)
    * :model:`materials.Lesson` (через поле `owner`)
    """
    username = None
    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=35, blank=True, null=True, verbose_name='Телефон')
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='Город')
    avatar = models.ImageField(upload_to='users/avatars/', blank=True, null=True, verbose_name='Аватар')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email

