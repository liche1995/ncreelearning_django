# Generated by Django 3.1.4 on 2021-04-23 16:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lesson_app', '0011_homeworkfiletable'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='homework',
            name='attach_file',
        ),
        migrations.RemoveField(
            model_name='homeworksubmit',
            name='attach_file',
        ),
    ]