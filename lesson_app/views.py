from django.shortcuts import render
from django.template.defaulttags import register
from lesson_app import models
import numpy as np

# Create your views here.


# 課程頁
def callesson(request):
    # 查詢結果
    ob = models.Lesson.objects.all()
    #v = [f.get_attname() for f in ob.meta.fields]
    # 抽取
    for a in ob:
        print(a.lseeonid)

    context = {}
    return render(request, "common/lesson.html", context)


# 資料庫存取
def querydb():

    return


# Django's range
@register.filter
def d_range(v):
    return range(v)
