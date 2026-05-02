"""
Management command to create demo data for the salon app.
Run: python manage.py setup_demo
"""
import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.utils import timezone
from apps.clients.models import Client
from apps.masters.models import Master, Service, MasterService
from apps.bookings.models import Booking
from apps.schedule.models import Schedule
from apps.payments.models import Payment
from apps.complaints.models import Complaint


class Command(BaseCommand):
    help = 'Создаёт демонстрационные данные и суперпользователя'

    def handle(self, *args, **options):
        # ── Группы ──────────────────────────────────────────────────────────
        admin_group, _ = Group.objects.get_or_create(name='Администратор')
        senior_group, _ = Group.objects.get_or_create(name='Старший администратор')
        self.stdout.write('Группы созданы.')

        # ── Суперпользователь ────────────────────────────────────────────────
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@nezhnost.ru', 'admin123')
            admin.first_name = 'Администратор'
            admin.save()
            self.stdout.write(self.style.SUCCESS('Суперпользователь admin / admin123 создан'))
        else:
            admin = User.objects.get(username='admin')
            self.stdout.write('Суперпользователь уже существует')

        # ── Услуги ───────────────────────────────────────────────────────────
        services_data = [
            # (name, category, duration, price, description)
            ('Маникюр классический',      'manicure', 60,  1500,  'Профессиональный уход за ногтями рук: обработка кутикулы, придание формы, полировка.'),
            ('Маникюр с гель-лаком',      'manicure', 90,  2500,  'Долговременное покрытие гель-лаком до 3 недель без сколов.'),
            ('Педикюр классический',      'manicure', 90,  2000,  'Полный уход за ногтями и кожей стоп.'),
            ('Педикюр с гель-лаком',      'manicure', 120, 3000,  'Педикюр + стойкое покрытие гель-лаком.'),
            ('Наращивание ногтей (гель)', 'manicure', 150, 3500,  'Моделирование формы и длины с использованием геля.'),
            ('Стрижка женская',           'hair',     60,  2000,  'Стрижка любой сложности + укладка феном.'),
            ('Стрижка мужская',           'hair',     45,  1200,  'Стрижка машинкой и ножницами, оформление бороды.'),
            ('Окрашивание волос',         'hair',     180, 5000,  'Профессиональное окрашивание красками Wella / Loreal.'),
            ('Мелирование волос',         'hair',     150, 4500,  'Классическое или балаяж-мелирование.'),
            ('Кератиновое выпрямление',  'hair',     180, 7000,  'Разглаживание и восстановление волос на 3–5 месяцев.'),
            ('Чистка лица',              'skin',     90,  3500,  'Глубокое очищение пор, пилинг, маска.'),
            ('Биоревитализация',         'skin',     60,  6000,  'Инъекционное увлажнение гиалуроновой кислотой.'),
            ('Микродермабразия',         'skin',     75,  4000,  'Аппаратная шлифовка и обновление кожи лица.'),
            ('Ламинирование ресниц',     'brows',    60,  3000,  'Придание изгиба, объёма и блеска натуральным ресницам.'),
            ('Наращивание ресниц',       'brows',    120, 4000,  'Наращивание по технике 1D–6D.'),
            ('Оформление бровей',        'brows',    45,  1200,  'Коррекция формы + окрашивание хной.'),
            ('Архитектура бровей',       'brows',    60,  1800,  'Построение идеальной формы с учётом черт лица.'),
            ('Макияж дневной',           'makeup',   60,  2500,  'Лёгкий натуральный макияж для повседневного образа.'),
            ('Макияж вечерний',          'makeup',   90,  3500,  'Насыщенный вечерний образ с акцентами.'),
            ('Макияж свадебный',         'makeup',   120, 5000,  'Стойкий брidal-макияж + пробный сеанс в подарок.'),
        ]

        services = []
        for name, category, duration, price, description in services_data:
            svc, created = Service.objects.get_or_create(
                name=name,
                defaults={
                    'category': category,
                    'duration_minutes': duration,
                    'price': price,
                    'description': description,
                    'is_active': True,
                }
            )
            services.append(svc)
            if created:
                self.stdout.write(f'  Услуга "{name}" создана')

        def svc(name):
            return Service.objects.filter(name=name).first()

        # ── Мастера ──────────────────────────────────────────────────────────
        masters_data = [
            (
                'Иванова Мария Петровна',
                'Мастер маникюра и педикюра',
                'Профессионал с 8-летним опытом работы в индустрии красоты. '
                'Специализируется на сложных дизайнах и наращивании ногтей. '
                'Победитель городского конкурса «Лучший мастер маникюра 2023».',
            ),
            (
                'Козлова Анна Сергеевна',
                'Стилист-колорист',
                'Дипломированный парикмахер с 10-летним стажем. '
                'Прошла обучение в академиях Wella и L\'Oréal Professionnel. '
                'Специализируется на окрашивании, кератиновом выпрямлении и женских стрижках.',
            ),
            (
                'Смирнова Екатерина Ивановна',
                'Косметолог-эстетист',
                'Косметолог высшей категории с медицинским образованием. '
                'Специализируется на аппаратной косметологии и инъекционных методиках. '
                'Опыт работы — 12 лет.',
            ),
            (
                'Петрова Ольга Владимировна',
                'Мастер бровей и ресниц',
                'Сертифицированный мастер по оформлению бровей и наращиванию ресниц. '
                'Работает по авторской методике создания «идеальной дуги». '
                'Победитель регионального чемпионата по бровям 2022.',
            ),
            (
                'Михайлова Светлана Андреевна',
                'Визажист',
                'Профессиональный визажист с опытом работы на съёмках и показах мод. '
                'Специализируется на свадебном и вечернем макияже. '
                'Подбирает макияж с учётом типа кожи и цветотипа.',
            ),
            (
                'Новикова Дарья Романовна',
                'Мастер маникюра',
                'Молодой специалист с 3-летним опытом. '
                'Сертифицированный мастер по технике гель-лак и дизайну ногтей. '
                'Работает чётко, аккуратно, с душой.',
            ),
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
                self.stdout.write(f'  Мастер "{full_name}" создан')

        def master(name_part):
            return Master.objects.filter(full_name__contains=name_part).first()

        # ── Привязка услуг к мастерам ─────────────────────────────────────
        assignments = {
            'Иванова': [
                'Маникюр классический', 'Маникюр с гель-лаком',
                'Педикюр классический', 'Педикюр с гель-лаком', 'Наращивание ногтей (гель)',
            ],
            'Козлова': [
                'Стрижка женская', 'Стрижка мужская',
                'Окрашивание волос', 'Мелирование волос', 'Кератиновое выпрямление',
            ],
            'Смирнова': [
                'Чистка лица', 'Биоревитализация', 'Микродермабразия',
            ],
            'Петрова': [
                'Ламинирование ресниц', 'Наращивание ресниц',
                'Оформление бровей', 'Архитектура бровей',
            ],
            'Михайлова': [
                'Макияж дневной', 'Макияж вечерний', 'Макияж свадебный',
            ],
            'Новикова': [
                'Маникюр классический', 'Маникюр с гель-лаком',
                'Педикюр классический',
            ],
        }

        for name_part, service_names in assignments.items():
            m = master(name_part)
            if m:
                for sname in service_names:
                    s = svc(sname)
                    if s:
                        MasterService.objects.get_or_create(master=m, service=s)

        # ── Клиенты ──────────────────────────────────────────────────────────
        clients_data = [
            ('client1', 'client1@nezhnost.ru', 'client123', 'Тестова Мария Ивановна',     '+7 (999) 123-45-67', ''),
            ('elena_v', 'elena@mail.ru',        'pass1234',  'Васильева Елена Николаевна', '+7 (916) 234-56-78', 'Аллергия на шеллак определённых марок'),
            ('oksana_k','oksana@yandex.ru',     'pass1234',  'Кузнецова Оксана Дмитриевна','+7 (926) 345-67-89', 'Предпочитает запись в утренние часы'),
            ('natasha', 'natasha@gmail.com',    'pass1234',  'Морозова Наталья Сергеевна', '+7 (903) 456-78-90', ''),
            ('irina_p', 'irina@inbox.ru',       'pass1234',  'Попова Ирина Александровна', '+7 (985) 567-89-01', 'Постоянный клиент с 2021 года'),
            ('julia',   'julia@list.ru',        'pass1234',  'Соколова Юлия Викторовна',   '+7 (915) 678-90-12', ''),
            ('anna_t',  'anna@bk.ru',           'pass1234',  'Тихонова Анна Олеговна',     '+7 (977) 789-01-23', 'Предпочитает мастера Иванову'),
            ('svetlana','sveta@mail.ru',        'pass1234',  'Лебедева Светлана Ивановна', '+7 (967) 890-12-34', ''),
            ('diana',   'diana@yandex.ru',      'pass1234',  'Панова Диана Рашидовна',     '+7 (906) 901-23-45', 'Первый визит'),
            ('karina',  'karina@gmail.com',     'pass1234',  'Фёдорова Карина Евгеньевна', '+7 (925) 012-34-56', ''),
        ]

        client_objects = []
        for username, email, password, full_name, phone, notes in clients_data:
            if not User.objects.filter(username=username).exists():
                u = User.objects.create_user(username, email, password)
                parts = full_name.split()
                u.last_name = parts[0]
                u.first_name = parts[1] if len(parts) > 1 else ''
                u.save()
            else:
                u = User.objects.get(username=username)

            c, created = Client.objects.get_or_create(
                phone=phone,
                defaults={
                    'user': u,
                    'full_name': full_name,
                    'email': email,
                    'notes': notes,
                }
            )
            client_objects.append(c)
            if created:
                self.stdout.write(f'  Клиент "{full_name}" создан')

        def client(name_part):
            return Client.objects.filter(full_name__contains=name_part).first()

        # ── Расписание мастеров (апрель–май 2025) ───────────────────────────
        today = datetime.date.today()
        schedule_masters = [
            master('Иванова'), master('Козлова'), master('Смирнова'),
            master('Петрова'), master('Михайлова'), master('Новикова'),
        ]

        # Генерируем расписание на ближайшие 14 дней и последние 14 дней
        schedule_days = []
        for delta in range(-14, 15):
            d = today + datetime.timedelta(days=delta)
            if d.weekday() < 6:  # пн–сб
                schedule_days.append(d)

        for m in schedule_masters:
            if not m:
                continue
            for d in schedule_days:
                if not Schedule.objects.filter(master=m, date=d).exists():
                    Schedule.objects.create(
                        master=m,
                        date=d,
                        start_time=datetime.time(9, 0),
                        end_time=datetime.time(19, 0),
                        status='approved',
                        created_by=admin,
                        approved_by=admin,
                        approved_at=timezone.now(),
                    )

        self.stdout.write('  Расписание создано')

        # ── Записи (бронирования) ─────────────────────────────────────────
        bookings_raw = [
            # (client_part, master_part, service_name, delta_days, hour, status)
            ('Тестова',    'Иванова',   'Маникюр с гель-лаком',      -10, 10, 'completed'),
            ('Васильева',  'Козлова',   'Стрижка женская',            -9,  11, 'completed'),
            ('Кузнецова',  'Смирнова',  'Чистка лица',                -8,  14, 'completed'),
            ('Морозова',   'Петрова',   'Оформление бровей',          -7,  12, 'completed'),
            ('Попова',     'Иванова',   'Маникюр классический',       -7,  16, 'completed'),
            ('Соколова',   'Михайлова', 'Макияж вечерний',            -6,  13, 'completed'),
            ('Тихонова',   'Козлова',   'Окрашивание волос',          -6,  10, 'completed'),
            ('Лебедева',   'Иванова',   'Педикюр классический',       -5,  11, 'completed'),
            ('Панова',     'Петрова',   'Ламинирование ресниц',       -5,  15, 'completed'),
            ('Фёдорова',   'Смирнова',  'Микродермабразия',           -4,  14, 'completed'),
            ('Тестова',    'Иванова',   'Педикюр с гель-лаком',       -3,  10, 'completed'),
            ('Васильева',  'Михайлова', 'Макияж свадебный',           -3,  12, 'completed'),
            ('Кузнецова',  'Петрова',   'Архитектура бровей',         -2,  16, 'completed'),
            ('Морозова',   'Козлова',   'Мелирование волос',          -2,  11, 'completed'),
            ('Попова',     'Смирнова',  'Биоревитализация',           -1,  14, 'completed'),
            ('Соколова',   'Новикова',  'Маникюр с гель-лаком',       -1,  10, 'completed'),
            ('Тихонова',   'Иванова',   'Наращивание ногтей (гель)',  -1,  15, 'completed'),
            ('Лебедева',   'Козлова',   'Кератиновое выпрямление',    0,   10, 'confirmed'),
            ('Панова',     'Иванова',   'Маникюр классический',       0,   13, 'arrived'),
            ('Фёдорова',   'Петрова',   'Наращивание ресниц',         0,   15, 'confirmed'),
            ('Тестова',    'Смирнова',  'Чистка лица',                1,   11, 'confirmed'),
            ('Васильева',  'Иванова',   'Маникюр с гель-лаком',       2,   12, 'confirmed'),
            ('Кузнецова',  'Михайлова', 'Макияж дневной',             2,   15, 'confirmed'),
            ('Морозова',   'Новикова',  'Педикюр классический',       3,   10, 'confirmed'),
            ('Попова',     'Козлова',   'Стрижка женская',            3,   14, 'confirmed'),
            ('Соколова',   'Петрова',   'Оформление бровей',          4,   11, 'pending'),
            ('Тихонова',   'Смирнова',  'Микродермабразия',           5,   13, 'pending'),
            ('Лебедева',   'Михайлова', 'Макияж вечерний',            6,   16, 'pending'),
            ('Панова',     'Новикова',  'Маникюр классический',       7,   10, 'pending'),
            ('Фёдорова',   'Иванова',   'Маникюр с гель-лаком',       7,   14, 'pending'),
        ]

        booking_objects = []
        for c_part, m_part, svc_name, delta, hour, status in bookings_raw:
            c = client(c_part)
            m = master(m_part)
            s = svc(svc_name)
            if not (c and m and s):
                continue
            d = today + datetime.timedelta(days=delta)
            start = datetime.time(hour, 0)
            end_dt = datetime.datetime.combine(d, start) + datetime.timedelta(minutes=s.duration_minutes)
            end = end_dt.time()

            b, created = Booking.objects.get_or_create(
                client=c,
                master=m,
                service=s,
                date=d,
                start_time=start,
                defaults={
                    'end_time': end,
                    'status': status,
                }
            )
            if not created:
                b.status = status
                b.end_time = end
                b.save()
            booking_objects.append((b, status))

        self.stdout.write(f'  Записей создано/обновлено: {len(booking_objects)}')

        # ── Платежи за выполненные записи ────────────────────────────────
        pay_methods = ['cash', 'card', 'cash', 'card', 'card', 'cash', 'card']
        idx = 0
        for b, status in booking_objects:
            if status == 'completed':
                if not Payment.objects.filter(booking=b).exists():
                    Payment.objects.create(
                        booking=b,
                        amount=b.service.price,
                        method=pay_methods[idx % len(pay_methods)],
                    )
                    idx += 1

        self.stdout.write('  Платежи созданы')

        # ── Жалобы ────────────────────────────────────────────────────────
        complaints_data = [
            (
                'Васильева', 0,
                'Мастер опоздала на 20 минут, не предупредила заранее. Пришлось ждать.',
                'closed', 'compensation',
                'Принесли извинения, предоставили скидку 15% на следующий визит.',
            ),
            (
                'Тихонова', 6,
                'Окрашивание получилось неравномерным — правая прядь заметно светлее.',
                'in_progress', None,
                'Связались с клиентом, назначена повторная процедура за счёт салона.',
            ),
            (
                'Панова', 8,
                'Не устроил результат ламинирования — ресницы выглядят склеенными.',
                'new', None,
                '',
            ),
        ]

        for c_part, booking_idx, text, status, resolution, admin_comment in complaints_data:
            c = client(c_part)
            if not c:
                continue
            related_booking = None
            completed = [b for b, st in booking_objects if st == 'completed' and b.client == c]
            if completed and booking_idx < len(completed):
                related_booking = completed[booking_idx]

            if not Complaint.objects.filter(client=c, text=text).exists():
                comp = Complaint.objects.create(
                    client=c,
                    booking=related_booking,
                    text=text,
                    status=status,
                    resolution=resolution,
                    admin_comment=admin_comment,
                    handled_by=admin if status != 'new' else None,
                )
                if status == 'closed':
                    comp.closed_at = timezone.now() - datetime.timedelta(days=1)
                    comp.save()

        self.stdout.write('  Жалобы созданы')

        self.stdout.write(self.style.SUCCESS('\n=== Демо-данные успешно созданы! ==='))
        self.stdout.write('Администратор: admin / admin123')
        self.stdout.write('Клиенты: client1 / client123, elena_v / pass1234 и др.')
