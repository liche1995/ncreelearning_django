from django.shortcuts import render
from django.template.defaulttags import register
from lesson_app import models
from django_pandas.io import read_frame


# 課程表
def callesson(request):
    # 查詢最新10筆資料
    lesson_result = models.Lesson.objects.all().order_by('-annouce_time')[:10]
    result_table = read_frame(lesson_result)

    context = {'result_table': result_table}
    return render(request, "common/lesson.html", context)


# 首頁存取
def for_index_page():
    # 取得資最新課程資料
    lesson_result = models.Lesson.objects.all().order_by('-annouce_time')[:6]
    lesson_result_table = read_frame(lesson_result)

    # 找尋對應封面照
    media_result = models.Multimedia.objects.filter(lesson_id__in=lesson_result_table['lessonid'], cover=1)
    media_result_table = read_frame(media_result)

    return lesson_result_table, media_result_table


# 詳細資料
def lesson_info(request):
    context = {}
    # 取得id資料
    lesson_id = int(request.GET.get("lessonid"))

    # 調閱lesson table
    db_resule = models.Lesson.objects.get(lessonid=lesson_id)

    # 整理輸出
    context['result'] = db_resule

    return render(request, "lesson/lesson_info.html", context)


# 新增課程
def new_lesson(request):
    context = {}
    if request.method.lower() == 'get':
        pass
    else:
        pass
    return render(request, "lesson/new_lesson.html", context)


# 修改課程
def edit_lesson(request):
    context = {}
    # 調閱資料
    if request.user.is_staff:
        table = _get_teacher_lesson()
    else:
        table = _get_teacher_lesson(request.user.id)

    return render(request, "lesson/lesson_table.html", context)


# 刪除課程
def delete_lesson(request):
    context = {}
    # 調閱資料
    if request.user.is_staff:
        table = _get_teacher_lesson()
    else:
        table = _get_teacher_lesson(request.user.id)


    return render(request, "lesson/lesson_table.html", context)


# 開課清單
def lesson_list(request):
    context = {}
    # 調閱資料
    if request.user.is_staff:
        table = _get_teacher_lesson()
    else:
        table = _get_teacher_lesson(request.user.id)

    return render(request, "lesson/lesson_table.html", context)


# inner function
def _get_teacher_lesson(userid: str = 0):
    if userid != 0:
        query = models.Lesson.objects.filter(auth=userid)
    else:
        query = models.Lesson.objects.all()

    result = read_frame(query)

    return result


# Django's range
@register.filter
def d_range(v):
    return range(v)
