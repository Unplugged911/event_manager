from django.db import models

class Event(models.Model):
    EVENT_TYPES = [
        ('conference', 'Конференция'),
        ('seminar', 'Семинар'),
        ('workshop', 'Мастер-класс'),
        ('other', 'Другое'),
    ]

    title = models.CharField(max_length=255, verbose_name="Название конференции", default="Без названия")
    type = models.CharField(max_length=50, choices=EVENT_TYPES, verbose_name="Тип мероприятия")
    date = models.DateTimeField(verbose_name="Дата и время проведения")
    location = models.CharField(max_length=255, verbose_name="Место проведения")
    description = models.TextField(verbose_name="Описание мероприятия")
    max_participants = models.PositiveIntegerField(verbose_name="Максимальное количество участников")
    participants_count = models.PositiveIntegerField(default=0, verbose_name="Количество участников")

    def __str__(self):
        return f"{self.type} - {self.date}"

class Participant(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="participants", verbose_name="Мероприятие")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    email = models.EmailField(verbose_name="Email")
    age = models.PositiveIntegerField(verbose_name="Возраст")
    university = models.CharField(max_length=255, verbose_name="Университет")
    faculty = models.CharField(max_length=255, verbose_name="Факультет")
    group = models.CharField(max_length=50, verbose_name="Группа")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"