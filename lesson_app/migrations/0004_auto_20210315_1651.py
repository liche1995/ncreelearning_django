# Generated by Django 3.1.4 on 2021-03-15 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lesson_app', '0003_multimedia_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='multimedia',
            name='file',
            field=models.FileField(null=True, upload_to='fileinfo/lesson_info', verbose_name='file'),
        ),
    ]