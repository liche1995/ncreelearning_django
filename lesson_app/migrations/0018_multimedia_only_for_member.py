# Generated by Django 3.1.4 on 2021-05-25 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lesson_app', '0017_multimedia_open_access'),
    ]

    operations = [
        migrations.AddField(
            model_name='multimedia',
            name='only_for_member',
            field=models.BooleanField(default=True, verbose_name='only_for_member'),
        ),
    ]
