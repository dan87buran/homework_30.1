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