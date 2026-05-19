import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')
django.setup()
from django.contrib.auth import get_user_model
from app.models import Status, Room
User = get_user_model()

s1, _ = Status.objects.get_or_create(name='Новая')
s2, _ = Status.objects.get_or_create(name='Мероприятие назначено')
s3, _ = Status.objects.get_or_create(name='Мероприятие завершено')


Room.objects.get_or_create(name='Переговорная А', defaults={'category': 'аудитория', 'capacity': 4, 'is_active': True})
Room.objects.get_or_create(name='Переговорная Б', defaults={'category': 'коворкинг', 'capacity': 6, 'is_active': True})
Room.objects.get_or_create(name='Конференц-зал',  defaults={'category': 'кинозал', 'capacity': 20, 'is_active': True})
Room.objects.get_or_create(name='Малый зал',      defaults={'category': 'кинозал', 'capacity': 2,  'is_active': False})

print('✅ БД заполнена! admin/admin, user1/user1')
