# Generated by Django 5.1.7 on 2025-03-15 01:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='title',
            field=models.CharField(default='Без названия', max_length=255, verbose_name='Название конференции'),
        ),
    ]
