# Generated by Django 3.1.4 on 2021-02-19 07:11

from django.db import migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uesrinfo',
            name='region',
            field=django_countries.fields.CountryField(max_length=3, verbose_name='region'),
        ),
    ]
