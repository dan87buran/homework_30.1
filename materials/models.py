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