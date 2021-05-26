# Generated by Django 3.1.4 on 2021-05-25 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lesson_app', '0018_multimedia_only_for_member'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='multimedia',
            name='only_for_member',
        ),
        migrations.AddField(
            model_name='multimedia',
            name='only_for_members',
            field=models.BooleanField(default=True, verbose_name='only_for_members'),
        ),
    ]