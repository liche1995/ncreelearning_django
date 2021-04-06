# Generated by Django 3.1.4 on 2021-04-06 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lesson_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='multimedia',
            name='file',
            field=models.FileField(null=True, upload_to='lesson_info', verbose_name='file'),
        ),
        migrations.AlterField(
            model_name='multimedia',
            name='image',
            field=models.ImageField(null=True, upload_to='lesson_info', verbose_name='image'),
        ),
    ]
