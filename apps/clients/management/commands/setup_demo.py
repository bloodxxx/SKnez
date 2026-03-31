"""
Management command to create demo data for the salon app.
Run: python manage.py setup_demo
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from apps.clients.models import Client
from apps.masters.models import Master, Service, MasterService


class Command(BaseCommand):
    help = 'Создаёт демонстрационные данные и суперпользователя'

    def handle(self, *args, **options):
        # Create groups
        admin_group, _ = Group.objects.get_or_create(name='Администратор')
        senior_group, _ = Group.objects.get_or_create(name='Старший администратор')
        self.stdout.write('Группы созданы.')

        # Create superuser
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@nezhnost.ru', 'admin123')
            admin.first_name = 'Администратор'
            admin.save()
            self.stdout.write(self.style.SUCCESS('Суперпользователь admin / admin123 создан'))
        else:
            self.stdout.write('Суперпользователь уже существует')

        # Create services
        services_data = [
            ('Маникюр классический', 60, 1500, 'Профессиональный уход за ногтями'),
            ('Маникюр с гель-лаком', 90, 2500, 'Долговременное покрытие гель-лаком'),
            ('Педикюр классический', 90, 2000, 'Уход за ногтями стоп'),
            ('Стрижка женская', 60, 2000, 'Стрижка и укладка'),
            ('Окрашивание волос', 180, 5000, 'Профессиональное окрашивание'),
            ('Ламинирование ресниц', 60, 3000, 'Придание изгиба и блеска ресницам'),
            ('Оформление бровей', 45, 1200, 'Коррекция и окрашивание'),
            ('Чистка лица', 90, 3500, 'Профессиональная чистка и уход'),
        ]

        services = []
        for name, duration, price, description in services_data:
            service, created = Service.objects.get_or_create(
                name=name,
                defaults={
                    'duration_minutes': duration,
                    'price': price,
                    'description': description,
                    'is_active': True,
                }
            )
            services.append(service)
            if created:
                self.stdout.write(f'Услуга "{name}" создана')

        # Create masters
        masters_data = [
            ('Иванова Мария Петровна', 'Мастер маникюра и педикюра', 'Профессионал с 8-летним опытом.'),
            ('Козлова Анна Сергеевна', 'Стилист-колорист', 'Специалист по окрашиванию и стрижкам.'),
            ('Смирнова Екатерина Ивановна', 'Мастер по уходу за лицом', 'Косметолог высшей категории.'),
            ('Петрова Ольга Владимировна', 'Мастер бровей и ресниц', 'Сертифицированный мастер.'),
        ]

        for full_name, specialization, bio in masters_data:
            master, created = Master.objects.get_or_create(
                full_name=full_name,
                defaults={
                    'specialization': specialization,
                    'bio': bio,
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f'Мастер "{full_name}" создан')

        # Assign services to masters
        masters = Master.objects.all()
        if masters.exists():
            # First master - manicure/pedicure
            m1 = Master.objects.filter(full_name__contains='Иванова').first()
            if m1:
                for svc in Service.objects.filter(name__in=['Маникюр классический', 'Маникюр с гель-лаком', 'Педикюр классический']):
                    MasterService.objects.get_or_create(master=m1, service=svc)

            # Second master - hair
            m2 = Master.objects.filter(full_name__contains='Козлова').first()
            if m2:
                for svc in Service.objects.filter(name__in=['Стрижка женская', 'Окрашивание волос']):
                    MasterService.objects.get_or_create(master=m2, service=svc)

            # Third master - face
            m3 = Master.objects.filter(full_name__contains='Смирнова').first()
            if m3:
                for svc in Service.objects.filter(name__in=['Чистка лица']):
                    MasterService.objects.get_or_create(master=m3, service=svc)

            # Fourth master - brows/lashes
            m4 = Master.objects.filter(full_name__contains='Петрова').first()
            if m4:
                for svc in Service.objects.filter(name__in=['Ламинирование ресниц', 'Оформление бровей']):
                    MasterService.objects.get_or_create(master=m4, service=svc)

        # Create demo client user
        if not User.objects.filter(username='client1').exists():
            client_user = User.objects.create_user('client1', 'client1@example.com', 'client123')
            client_user.first_name = 'Мария'
            client_user.last_name = 'Тестова'
            client_user.save()
            Client.objects.get_or_create(
                user=client_user,
                defaults={
                    'full_name': 'Тестова Мария Ивановна',
                    'phone': '+7 (999) 123-45-67',
                    'email': 'client1@example.com',
                }
            )
            self.stdout.write(self.style.SUCCESS('Тестовый клиент client1 / client123 создан'))

        self.stdout.write(self.style.SUCCESS('\n=== Демо-данные успешно созданы! ==='))
        self.stdout.write('Администратор: admin / admin123')
        self.stdout.write('Клиент: client1 / client123')
