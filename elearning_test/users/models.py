from django.db import models
from django_countries.fields import CountryField


# Create your models here.
class UesrInfo(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name='id')
    username = models.CharField(max_length=150, unique=True, verbose_name='username')
    last_name = models.CharField(max_length=150, unique=False, verbose_name='last_name')
    first_name = models.CharField(max_length=150, unique=False, verbose_name='first_name')
    address = models.CharField(max_length=150, unique=False, verbose_name='address')
    email = models.CharField(max_length=150, unique=False, verbose_name='email')
    telephone = models.CharField(max_length=150, unique=False, verbose_name='telephone')
    region = CountryField(max_length=3, unique=False, verbose_name='region')

