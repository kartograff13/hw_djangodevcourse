from urllib.parse import urlparse

from rest_framework.exceptions import ValidationError


def validate_youtube_url(value):
    """Функция проверяет, что ссылка ведёт на 'Youtube'"""
    if not value:
        return

    parsed = urlparse(value)
    hostname = parsed.hostname

    if not hostname:
        raise ValidationError("Некорректный URL")

    allowed_domains = [
        "youtube.com",
        "www.youtube.com",
        "youtu.be",
        "m.youtube.com",
    ]

    if hostname not in allowed_domains:
        raise ValidationError("Разрешены только ссылки на 'Youtube'.")
