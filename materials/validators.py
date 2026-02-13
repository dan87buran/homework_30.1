import re
from rest_framework.serializers import ValidationError
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError as DjangoValidationError

def validate_youtube_link(value):
    """
    Проверяет, что ссылка ведёт на youtube.com или youtu.be.
    """
    # Сначала проверяем, что это вообще корректный URL
    url_validator = URLValidator()
    try:
        url_validator(value)
    except DjangoValidationError:
        raise ValidationError("Некорректный URL.")

    # Допустимые домены YouTube
    allowed_domains = ['youtube.com', 'youtu.be']
    if not any(domain in value for domain in allowed_domains):
        raise ValidationError("Ссылка должна быть на youtube.com или youtu.be.")

    return value