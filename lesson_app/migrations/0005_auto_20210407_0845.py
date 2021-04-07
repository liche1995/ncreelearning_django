# Generated by Django 3.1.4 on 2021-04-07 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lesson_app', '0004_auto_20210407_0842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='multimedia',
            name='file',
            field=models.FileField(null=True, upload_to='fileinfo/lesson_info', verbose_name='file'),
        ),
        migrations.AlterField(
            model_name='multimedia',
            name='image',
            field=models.ImageField(null=True, upload_to='fileinfo/lesson_info', verbose_name='image'),
        ),
    ]
