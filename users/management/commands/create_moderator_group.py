from django.contrib.auth.models import Group
from django.core.management import BaseCommand


class Command(BaseCommand):
    """Создаёт группу модераторов"""

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name="Модераторы")

        if created:
            self.stdout.write(self.style.SUCCESS("Группа 'Модераторы' создана."))
        else:
            self.stdout.write(self.style.SUCCESS("Группа 'Модераторы' уже существует."))
