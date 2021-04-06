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
    lessonid = models.AutoField(primary_key=True, help_text='課程ID編號，自動產生')
    name = models.CharField(max_length=45, help_text='課程名稱')
    lessontype = models.CharField(max_length=45, help_text='課程種類')
    auth = models.IntegerField(help_text='建立者', default=0)
    situation = models.CharField(max_length=15, help_text='實體、線上或兩者皆有')
    statue = models.BooleanField(default=False)
    annouce_time = models.DateTimeField()
    start_time = models.DateTimeField()
    finish_time = models.DateTimeField(blank=True, null=True)
    lessoninfo = models.CharField(max_length=300)
    certificate = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'lesson'


# 學生清單
class Studentlist(models.Model):
    inner_id = models.AutoField(primary_key=True, verbose_name='id')
    student_id = models.IntegerField(verbose_name='student_id')
    lesson_id = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name='lesson_id')
    first_name = models.CharField(max_length=150, verbose_name='first_name')
    last_name = models.CharField(max_length=150, verbose_name='last_name')
    lesson_situation = models.CharField(max_length=150, verbose_name='lesson_situation', null=True)


# 多媒體資料
class Multimedia(models.Model):
    media_id = models.AutoField(primary_key=True, verbose_name="id")
    lesson_id = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name="lesson_id")
    cover = models.BooleanField(verbose_name='cover', default=False)
    media_type = models.IntegerField(verbose_name="media_type", help_text="file:0 picture:1 vided:2")
    file = models.FileField(verbose_name='file', upload_to='fileinfo/lesson_info', null=True)
    image = models.ImageField(verbose_name='image', upload_to='fileinfo/lesson_info', null=True)
    filename = models.CharField(max_length=150, verbose_name='filename')


class LessonTable(models.Model):
    inner_id = models.AutoField(primary_key=True, verbose_name='inner_id')
    lesson_id = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name='lesson_id')
    ch = models.IntegerField(default=0)
    sb = models.IntegerField(default=0)
    title = models.CharField(max_length=150, null=True)

    class Meta:
        db_table = 'lesson_table'


