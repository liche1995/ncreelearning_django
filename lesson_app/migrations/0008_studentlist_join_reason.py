# Generated by Django 3.1.4 on 2021-04-15 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lesson_app', '0007_studentlist_agree'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentlist',
            name='join_reason',
            field=models.CharField(max_length=300, null=True, verbose_name='join_reason'),
        ),
    ]
