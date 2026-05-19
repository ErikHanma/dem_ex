from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date, timedelta

#модель пользователя
class User(AbstractUser):
    patronymic = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)

#модель статуса бронирования помещения
class Status(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self): return self.name

#модель самого помещения (комнаты)
class Room(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    capacity = models.IntegerField(default=0)
    image = models.ImageField(upload_to='rooms/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name
    def is_available(self): return self.is_active


#модель создания бронирования помещения
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    payment = models.CharField(max_length=50, blank=True)
    comment = models.TextField(blank=True)
    review = models.TextField(blank=True)
    @property
    def can_cancel(self): return self.date > date.today() + timedelta(days=1)