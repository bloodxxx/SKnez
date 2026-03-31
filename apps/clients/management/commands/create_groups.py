from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Создаёт группы пользователей: Администратор и Старший администратор'

    def handle(self, *args, **options):
        admin_group, created = Group.objects.get_or_create(name='Администратор')
        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Администратор" создана'))
        else:
            self.stdout.write('Группа "Администратор" уже существует')

        senior_group, created = Group.objects.get_or_create(name='Старший администратор')
        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Старший администратор" создана'))
        else:
            self.stdout.write('Группа "Старший администратор" уже существует')

        self.stdout.write(self.style.SUCCESS('Готово!'))
