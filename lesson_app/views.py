from django.shortcuts import render
from django.template.defaulttags import register
from lesson_app import models
from django_pandas.io import read_frame

# Create your views here.


# 課程表
def callesson(request):
    # 查詢最新10筆資料
    lesson_result = models.Lesson.objects.all().order_by('-annouce_time')[:10]
    result_table = read_frame(lesson_result)

    context = {'result_table': result_table}
    return render(request, "common/lesson.html", context)


# 首頁存取
def for_index_page():
    lesson_result = models.Lesson.objects.all().order_by('-annouce_time')[:9]
    result_table = read_frame(lesson_result)
    return result_table


# 詳細資料
def lesson_info(request):
    content = {}
    return render(request, "lesson/lesson_info.html", content)


# Django's range
@register.filter
def d_range(v):
    return range(v)
