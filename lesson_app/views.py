from django.shortcuts import render
from django.template.defaulttags import register
from lesson_app import models
from django_pandas.io import read_frame

# Create your views here.


# 課程頁
def callesson(request):
    # 查詢最新5筆資料
    lesson_result = models.Lesson.objects.all().order_by('-annouce_time')[:5]
    result_table = read_frame(lesson_result)

    context = {'result_table': result_table}
    return render(request, "common/lesson.html", context)


# 資料庫存取
def querydb():

    return


# Django's range
@register.filter
def d_range(v):
    return range(v)
