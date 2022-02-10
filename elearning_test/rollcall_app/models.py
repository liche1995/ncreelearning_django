from django.db import models
from lesson_app.models import LessonTable


# 點名簽到
class Rollcall(models.Model):
    inner_id = models.AutoField(primary_key=True)
    lessontableid = models.ForeignKey(LessonTable, on_delete=models.CASCADE, verbose_name='lessontable_id', default=0)
    user_id = models.IntegerField(null=False, verbose_name='user_id')
    sign_in_time = models.DateTimeField(verbose_name='sign_in_time')

    class Meta:
        db_table = 'rollcall'
