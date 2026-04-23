import os

from celery import Celery

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("hw_djangodevcourse")

# Загружаем настройки из Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматически находим задачи в приложениях проекта
app.autodiscover_tasks()
