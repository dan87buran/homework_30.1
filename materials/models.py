from django.db import models
from django.conf import settings


class Course(models.Model):
    """
    Модель курса.

    **Поля**
    * ``title`` — название курса.
    * ``preview`` — превью-изображение.
    * ``description`` — описание.
    * ``owner`` — владелец курса (:model:`users.User`).

    Связанные модели:
    * :model:`materials.Lesson` (через related_name='lessons')
    """
    objects = None
    title = models.CharField(max_length=200, verbose_name='Название')
    preview = models.ImageField(upload_to='courses/previews/', blank=True, null=True, verbose_name='Превью')
    description = models.TextField(verbose_name='Описание')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name='Владелец',
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'

    def __str__(self):
        return self.title


class Lesson(models.Model):
    """
    Модель урока.

    **Поля**
    * ``title`` — название урока.
    * ``description`` — описание.
    * ``preview`` — превью-изображение.
    * ``video_link`` — ссылка на видео.
    * ``course`` — курс, к которому принадлежит урок (:model:`materials.Course`).
    * ``owner`` — владелец урока (:model:`users.User`).
    """
    objects = None
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    preview = models.ImageField(upload_to='lessons/previews/', blank=True, null=True, verbose_name='Превью')
    video_link = models.URLField(verbose_name='Ссылка на видео')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name='Курс')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Владелец',
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'

    def __str__(self):
        return self.title

class Subscription(models.Model):
    objects = None
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')   # чтобы не было дублей
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.email} -> {self.course.title}'

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('paid', 'Оплачен'),
        ('canceled', 'Отменён'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    course = models.ForeignKey('Course', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Курс')
    lesson = models.ForeignKey('Lesson', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Урок')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    session_id = models.CharField(max_length=255, verbose_name='ID сессии Stripe', blank=True, null=True)
    payment_url = models.URLField(max_length=500, verbose_name='Ссылка на оплату', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f'{self.user} - {self.amount}'

    class Meta:
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'