from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class UesrInfoExtend(AbstractUser):
    address = models.CharField(max_length=150, unique=False, verbose_name='address')
    region = models.CharField(max_length=3, unique=False, verbose_name='region')
