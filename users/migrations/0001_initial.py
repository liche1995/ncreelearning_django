# Generated by Django 3.1.4 on 2021-02-19 02:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UesrInfo',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, verbose_name='id')),
                ('username', models.CharField(max_length=150, unique=True, verbose_name='username')),
                ('last_name', models.CharField(max_length=150, verbose_name='last_name')),
                ('first_name', models.CharField(max_length=150, verbose_name='first_name')),
                ('address', models.CharField(max_length=150, verbose_name='address')),
                ('email', models.CharField(max_length=150, verbose_name='email')),
                ('telephone', models.CharField(max_length=150, verbose_name='telephone')),
                ('region', models.CharField(max_length=3, verbose_name='region')),
            ],
        ),
    ]
