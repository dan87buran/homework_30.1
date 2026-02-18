from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone

from .models import Course, Subscription

User = get_user_model()

@shared_task
def send_course_update_email(course_id):
    """
    Отправляет уведомления всем подписчикам курса о его обновлении.
    """
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return f"Курс с id {course_id} не найден"

    # Получаем список email всех подписчиков
    subscriptions = Subscription.objects.filter(course=course).select_related('user')
    emails = [sub.user.email for sub in subscriptions if sub.user.email]

    if not emails:
        return f"Нет подписчиков с email для курса {course.title}"

    subject = f"Курс '{course.title}' был обновлен"
    message = f"Курс '{course.title}' был обновлен. Зайдите на платформу, чтобы посмотреть изменения."
    from_email = settings.DEFAULT_FROM_EMAIL  # нужно определить в settings.py

    send_mail(subject, message, from_email, emails)
    return f"Уведомления отправлены {len(emails)} подписчикам курса {course.title}"

@shared_task
def deactivate_inactive_users():
    """
    Деактивирует пользователей, которые не заходили более 30 дней.
    """
    month_ago = timezone.now() - timedelta(days=30)
    # Ищем активных пользователей, которые либо никогда не заходили (last_login=None),
    # либо заходили раньше чем месяц назад
    inactive_users = User.objects.filter(
        is_active=True,
        last_login__lt=month_ago
    )
    count = inactive_users.update(is_active=False)
    return f"Деактивировано {count} неактивных пользователей"