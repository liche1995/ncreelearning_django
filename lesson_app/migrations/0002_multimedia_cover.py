# Generated by Django 3.1.4 on 2021-03-12 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lesson_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='multimedia',
            name='cover',
            field=models.BooleanField(default=False, verbose_name='cover'),
        ),
    ]