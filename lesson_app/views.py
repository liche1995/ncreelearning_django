from django.shortcuts import render
from django.template.defaulttags import register
from lesson_app import models
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django_pandas.io import read_frame
import pandas as pd
import numpy as np
from distutils.util import strtobool
from datetime import datetime


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

    # 抽取id
    key_id = media_result_table['lesson_id'].str.findall('\d+')
    for i in range(key_id.shape[0]):
        media_result_table.loc[i, 'key_id'] = int(key_id.iloc[i][0])

    # merge
    table = pd.merge(lesson_result_table, media_result_table, left_on='lessonid', right_on='key_id', how='left')
    # 處裡空值
    table["key_id"] = table["key_id"].fillna(np.iinfo(np.int64).min)
    table["key_id"] = table["key_id"].astype('int64')

    return table


# 詳細資料
def lesson_info(request):
    context = {}
    # 取得id資料
    lesson_id = int(request.GET.get("lessonid"))

    # 調閱lesson table
    info = models.Lesson.objects.get(lessonid=lesson_id)
    table = read_frame(models.LessonTable.objects.filter(lesson_id_id=lesson_id))
    media = read_frame(models.Multimedia.objects.filter(lesson_id_id=lesson_id))
    cover = read_frame(models.Multimedia.objects.filter(lesson_id_id=lesson_id, cover=1))
    teacher = auth.models.User.objects.get(id=info.auth)

    # 整理輸出
    context['info'] = info
    context['table'] = table
    context['media'] = media
    context['cover'] = cover
    context['teacher'] = teacher

    return render(request, "lesson/lesson_info.html", context)


# 新增課程
@login_required
def new_lesson(request):
    context = {}
    if request.method.lower() == 'get':
        context["today"] = datetime.today()
        return render(request, "lesson/new_lesson.html", context)
    else:
        # 固定資料
        name = request.POST.get('lessoname', '')
        lessontype = request.POST.get('lessontype', '')
        auth = request.user.id
        situation = request.POST.get('lesson_mode', '')
        statue = strtobool(request.POST.get('statue', ''))
        annouce_time = request.POST.get('annouce_time', '')
        start_time = request.POST.get('start_time', '')
        finish_time = request.POST.get('finish_time', '')
        lessoninfo = request.POST.get('lessoninfo', '')
        certificate = strtobool(request.POST.get('sing_licnese', ''))

        # 動態變化資料
        lesson_count = int(request.POST.get("lesson_count", ""))
        lesson_id_count = int(request.POST.get("lesson_id_count", ""))
        # 課程表
        lesson_table = _creat_lesson_table(request, lesson_count, lesson_id_count)

        # 輸入資料庫
        # 基本資料輸入
        new = models.Lesson.objects.create(name=name, lessontype=lessontype, auth=auth, situation=situation, statue=statue,
                                           annouce_time=annouce_time, start_time=start_time, finish_time=finish_time,
                                           lessoninfo=lessoninfo, certificate=certificate)
        new.save()
        # 課程表資料輸入
        for i in range(lesson_table.shape[0]):
            models.LessonTable.objects.create(lesson_id_id=new.lessonid,
                                              ch=int(lesson_table["chapter"][i]),
                                              sb=int(lesson_table["submit"][i]),
                                              title=lesson_table["title"][i])
        # 課程封面輸入
        models.Multimedia.objects.create(lesson_id_id=new.lessonid, cover=1,
                                         media_type=1, image=request.FILES['cover'], filename=request.FILES['cover'].name)

        context["lessonid"] = new.lessonid
        return render(request, "lesson/created_lesson.html", context)


# 修改課程
@login_required
def edit_lesson(request):
    context = {}
    # 調閱資料
    if request.user.is_staff:
        table = _get_teacher_lesson()
    else:
        table = _get_teacher_lesson(request.user.id)

    return render(request, "lesson/lesson_table.html", context)


# 刪除課程
@login_required
def delete_lesson(request):
    context = {}
    # 調閱資料
    if request.user.is_staff:
        table = _get_teacher_lesson()
    else:
        table = _get_teacher_lesson(request.user.id)


    return render(request, "lesson/lesson_table.html", context)


# 開課清單
@login_required
def lesson_list(request):
    context = {}
    # 調閱資料
    if request.user.is_staff:
        table = _get_teacher_lesson()
    else:
        table = _get_teacher_lesson(request.user.id)

    return render(request, "lesson/lesson_table.html", context)


# 參加課程
@login_required
def join_lesson(request):
    context = {}
    # 資料調閱
    lessoninfo = models.Lesson.objects.get(lessonid=int(request.GET.get('lessonid')))
    in_class = _already_in_lesson(int(request.user.id), int(request.GET.get('lessonid')))

    # 判斷參加或退出
    if in_class:
        context["situation"] = "in"

    elif request.GET.get('situation') is not None:
        if request.GET.get('situation') == "online":



            print("online")
        else:




            print("entity")
    else:
        # 取得授課模式
        situation = lessoninfo.situation
        context["situation"] = situation
        context["lessonid"] = lessoninfo.lessonid

        ## 線上
        #if situation is 'online':
        #    models.Studentlist.objects.create(student_id=request.user.id,lesson_id=int(request.GET.get('lessonid')),
        #                                      first_name=request.user.first_name,last_name=request.user.last_name,
        #                                      lesson_situation='online')
        ## 實體
        #elif situation is 'entity':
        #    models.Studentlist.objects.create(student_id=request.user.id,lesson_id=int(request.GET.get('lessonid')),
        #                                      first_name=request.user.first_name,last_name=request.user.last_name,
        #                                      lesson_situation='entity')

        ## 兩者皆有
        #else:
        #    models.Studentlist.objects.create(student_id=request.user.id,lesson_id=int(request.GET.get('lessonid')),
        #                                      first_name=request.user.first_name,last_name=request.user.last_name,
        #                                      lesson_situation='both')



    return render(request, "lesson/joinorquit.html", context)

# 參加或退出
def join_or_quit(request):

    return



# inner function
def _get_teacher_lesson(userid: str = 0):
    if userid != 0:
        query = models.Lesson.objects.filter(auth=userid)
    else:
        query = models.Lesson.objects.all()

    result = read_frame(query)

    return result


def _already_in_lesson(student_id: int, lesson_id: int):
    try:
        query = models.Studentlist.objects.get(student_id=student_id, lesson_id=lesson_id)
        return True
    except models.Studentlist.DoesNotExist:
        return False


def _creat_lesson_table(requese, size, count_str):
    df = pd.DataFrame(columns=['chapter', 'submit', 'title'])
    for i in range(count_str+1):
        ch_index = 'ch' + str(i)
        sb_index = 'sb' + str(i)
        title_index = 'title' + str(i)

        if requese.POST.get(ch_index) is not None:
            if requese.POST.get(ch_index) == "":
                ch = 0
            else:
                ch = requese.POST.get(ch_index)
            if requese.POST.get(sb_index) == "":
                sb = 0
            else:
                sb = requese.POST.get(sb_index)

            title = requese.POST.get(title_index)
            df = df.append({'chapter': ch, 'submit': sb, 'title': title}, ignore_index=True)

    # 重新排列
    df = df.sort_values(by=['chapter', 'submit'])
    return df


# Django's range
@register.filter
def d_range(v):
    return range(v)
