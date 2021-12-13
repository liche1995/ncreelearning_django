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
    verify = models.BooleanField(default=False, help_text='審查參加人員')
    annouce_time = models.DateTimeField()
    start_time = models.DateTimeField()
    finish_time = models.DateTimeField(blank=True, null=True)
    lessoninfo = models.CharField(max_length=300)
    certificate = models.BooleanField(default=False)
    address = models.CharField(max_length=300, default='online mode')
    objects = models.Manager()

    # return dictionary
    def to_dict(self):
        return_data = {
            "lessonid": self.lessonid,
            "name": self.name,
            "lessontype": self.lessontype,
            "auth": self.auth,
            "situation": self.situation,
            "verify": self.verify,
            "annouce_time": self.annouce_time,
            "start_time": self.start_time,
            "finish_time": self.finish_time,
            "lessoninfo": self.lessoninfo,
            "certificate": self.certificate,
            "address": self.address,
        }
        return return_data

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
    agree = models.BooleanField(verbose_name='agree', default=True)
    join_reason = models.CharField(max_length=300, verbose_name='join_reason', null=True)
    objects = models.Manager()

    class Meta:
        db_table = 'lesson_studentlist'


# 多媒體資料
def path_return(instance, filename):
    # 針對封面
    if instance.cover:
        setting_path = "lesson_info/{0}/cover/{1}".format(str(instance.lesson_id_id), filename)
    # 針對教材
    elif instance.textbook:
        setting_path = "lesson_info/{0}/textbook/{1}".format(str(instance.lesson_id_id), filename)
    else:
        setting_path = "lesson_info/{0}".format(filename)
    return setting_path


class Multimedia(models.Model):
    media_id = models.AutoField(primary_key=True, verbose_name="id")
    lesson_id = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name="lesson_id")
    cover = models.BooleanField(verbose_name='cover', default=False)
    textbook = models.BooleanField(verbose_name='textbook', default=False)
    media_type = models.IntegerField(verbose_name="media_type", help_text="file:0 picture:1 vided:2")
    file = models.FileField(verbose_name='file', upload_to=path_return, null=True)
    image = models.ImageField(verbose_name='image', upload_to=path_return, null=True)
    external_source = models.CharField(max_length=500, verbose_name='external_source', null=True)
    filename = models.CharField(max_length=150, verbose_name='filename')
    open_access = models.BooleanField(verbose_name="open_access", default=True)
    only_for_members = models.BooleanField(verbose_name="only_for_members", default=True)
    objects = models.Manager()

    # 回傳一般檔案名稱
    def filename_without_extension(self):
        filename = self.filename.split(".")[0]
        return filename

    # 回傳副檔名
    def file_extension(self):
        extension = self.filename.split(".")[1]
        return extension

    class Meta:
        db_table = 'lesson_multimedia'


# 課綱表
class LessonTable(models.Model):
    inner_id = models.AutoField(primary_key=True, verbose_name='inner_id')
    lesson_id = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name='lesson_id')
    ch = models.IntegerField(default=0)
    sb = models.IntegerField(default=0)
    title = models.CharField(max_length=150, null=True)
    objects = models.Manager()

    class Meta:
        db_table = 'lesson_table'


# 教材連接表
class LessonRelatedMedia(models.Model):
    inner_id = models.AutoField(primary_key=True, null=False)
    lesson_id = models.IntegerField(null=False)
    t_id = models.ForeignKey(LessonTable, on_delete=models.CASCADE, null=False)
    media_id = models.OneToOneField(Multimedia, on_delete=models.CASCADE, null=False)
    objects = models.Manager()

    class Meta:
        db_table = "lesson_related_media"


# 習題列表
class Homework(models.Model):
    inner_id = models.AutoField(primary_key=True, verbose_name='inner_id')
    lessontable_id = models.ForeignKey(LessonTable, on_delete=models.CASCADE, verbose_name='lesson_table_id')
    lesson_id = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name='lesson_id')
    title = models.CharField(max_length=150, null=False, verbose_name='title')
    homeworkinfo = models.CharField(max_length=300, null=True, verbose_name='homeworkinfo')
    attach_file_exist = models.BooleanField(default=False, verbose_name='attach_file_exist')
    start_time = models.DateField(default='1900-01-01', null=False, verbose_name='start_time')
    finish_time = models.DateField(default='9999-12-31', verbose_name='finish_time')
    turn_it_available = models.BooleanField(default=False, verbose_name='turn_it_available')
    objects = models.Manager()

    class Meta:
        db_table = 'homework'


# 習題附檔
def homework_file_path_return(instance, filename):
    filepath = "lesson_homework_file/{0}/{1}".format(str(instance.homeworkid_id), filename)
    return filepath


class HomeworkAttachFile(models.Model):
    inner_id = models.AutoField(primary_key=True, verbose_name="inner_id")
    homeworkid = models.ForeignKey(Homework, on_delete=models.CASCADE, verbose_name="homework_id")
    file = models.FileField(verbose_name='file', upload_to=homework_file_path_return, null=True)
    open_access = models.BooleanField(verbose_name="open_access", default=False)
    only_for_members = models.BooleanField(verbose_name="only_for_members", default=False)
    objects = models.Manager()

    # 回傳一般檔案名稱
    def filename_without_extension(self):
        import re
        filename = re.split("[/.]", self.file.name)[-2]
        return filename

    # 回傳檔案名稱
    def filename(self):
        filename = self.file.name.split("/")[-1]
        return filename

    class Meta:
        db_table = "homework_attach_file"


# 繳交作業資料
class HomeworkSubmit(models.Model):
    inner_id = models.AutoField(primary_key=True, verbose_name='inner_id')
    lessontable_id = models.ForeignKey(LessonTable, on_delete=models.CASCADE, verbose_name='lesson_table_id')
    lesson_id = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name='lesson_id')
    homework_id = models.ForeignKey(Homework,
                                    on_delete=models.CASCADE, verbose_name='homework_id', null=False, default=-9)
    user_id = models.IntegerField(null=False, verbose_name='user_id')
    submitinfo = models.CharField(max_length=300, null=True, verbose_name='submitinfo')
    attach_file_exist = models.BooleanField(default=False, verbose_name='attach_file_exist')
    submit_time = models.DateTimeField("submit_time", auto_now_add=True)
    score = models.IntegerField(null=True, verbose_name="score")
    objects = models.Manager()

    class Meta:
        db_table = 'homeworksubmit'


# 習題檔案表
def homework_submit_file_path_return(instance, filename):
    filepath = "lesson_homework_submit_file/{0}/{1}/{2}".\
        format(str(instance.homeworksubmit_id.homework_id_id), str(instance.homeworksubmit_id.user_id), filename)
    return filepath


class HomeworkFileTable(models.Model):
    inner_id = models.AutoField(primary_key=True, verbose_name='inner_id')
    lesson_id = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name='lesson_id', default=0)
    lessontable_id = models.ForeignKey(LessonTable, on_delete=models.CASCADE, verbose_name='lesson_table_id', default=0)
    homeworksubmit_id = models.ForeignKey(HomeworkSubmit,
                                          on_delete=models.CASCADE, verbose_name='homeworksubmit_id', null=True)
    file = models.FileField(verbose_name="file", null=True, upload_to=homework_submit_file_path_return)
    open_access = models.BooleanField(verbose_name="open_access", default=False)
    only_for_members = models.BooleanField(verbose_name="only_for_members", default=False)
    objects = models.Manager()

    # 回傳一般檔案名稱
    def filename_without_extension(self):
        import re
        filename = re.split("[/.]", self.file.name)[-2]
        return filename

    # 回傳檔案名稱
    def filename(self):
        filename = self.file.name.split("/")[-1]
        return filename

    class Meta:
        db_table = 'homeworkfiletable'
