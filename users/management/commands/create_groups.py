from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Создаёт группу "Модераторы"'

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='Модераторы')
        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Модераторы" успешно создана'))
        else:
            self.stdout.write('Группа "Модераторы" уже существует')