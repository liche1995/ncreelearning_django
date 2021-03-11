# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


# get Lesson table data
class Lesson(models.Model):
    lessonid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    lessontype = models.CharField(max_length=45)
    auth = models.IntegerField()
    situation = models.IntegerField()
    annouce_time = models.DateTimeField()
    start_time = models.DateTimeField()
    finish_time = models.DateTimeField(blank=True, null=True)
    lessoninfo = models.CharField(max_length=300)

    class Meta:
        managed = False
        db_table = 'lesson'


# 學生清單
class Studentlist(models.Model):
    student_id = models.IntegerField(verbose_name='id')
    lesson_id = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name='lesson_id')
    first_name = models.CharField(max_length=150, verbose_name='first_name')
    last_name = models.CharField(max_length=150, verbose_name='last_name')


# 多媒體資料
class Multimedia(models.Model):
    media_id = models.AutoField(primary_key=True, verbose_name="id")
    media_type = models.IntegerField(verbose_name="media_type")
    lesson_id = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name="lesson_id")
    filename = models.CharField(max_length=150, verbose_name='filename')


