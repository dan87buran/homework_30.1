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


class Payment(models.Model):
    """
    Модель платежа.

    **Поля**
    * ``user`` — ссылка на :model:`users.User`.
    * ``payment_date`` — дата и время оплаты.
    * ``course`` — оплаченный курс (:model:`materials.Course`), может быть NULL.
    * ``lesson`` — оплаченный урок (:model:`materials.Lesson`), может быть NULL.
    * ``amount`` — сумма платежа.
    * ``payment_method`` — способ оплаты (cash/transfer).

    **Ограничения**
    * Хотя бы одно из полей ``course`` или ``lesson`` должно быть заполнено.
    """
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Наличные'),
        ('transfer', 'Перевод на счет'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Пользователь'
    )
    payment_date = models.DateTimeField(verbose_name='Дата оплаты')
    course = models.ForeignKey(
        'materials.Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Оплаченный курс'
    )
    lesson = models.ForeignKey(
        'materials.Lesson',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Оплаченный урок'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма оплаты')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, verbose_name='Способ оплаты')

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_date']

    def __str__(self):
        return f'{self.user} - {self.payment_date} - {self.amount}'