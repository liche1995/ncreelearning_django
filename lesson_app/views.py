from django.shortcuts import render
from django.template.defaulttags import register
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django_pandas.io import read_frame
import pandas as pd
import numpy as np
from distutils.util import strtobool
from datetime import datetime
from lesson_app import models


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

    # 有資料
    if media_result_table.shape[0] > 0:
        # 抽取id
        key_id = media_result_table['lesson_id'].str.findall('\d+')
        for i in range(key_id.shape[0]):
            media_result_table.loc[i, 'key_id'] = int(key_id.iloc[i][0])

        # merge
        table = pd.merge(lesson_result_table, media_result_table, left_on='lessonid', right_on='key_id', how='left')
        # 處理空值
        table["key_id"] = table["key_id"].fillna(np.iinfo(np.int64).min)
        table["key_id"] = table["key_id"].astype('int64')
    else:
        table = lesson_result_table.copy()
        for i in range(len(media_result_table.columns)):
            table[media_result_table.columns[i]] = np.iinfo(np.int64).min
            table[media_result_table.columns[i]] = table[media_result_table.columns[i]].astype('int64')
        table["key_id"] = np.iinfo(np.int64).min
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
        address = request.POST.get('address', 'online mode')

        # 動態變化資料
        lesson_count = int(request.POST.get("lesson_count", ""))
        lesson_id_count = int(request.POST.get("lesson_id_count", ""))
        # 課程表
        lesson_table = _creat_lesson_table(request, lesson_count, lesson_id_count)

        # 輸入資料庫
        # 基本資料輸入
        new = models.Lesson.objects.create(name=name, lessontype=lessontype, auth=auth, situation=situation, statue=statue,
                                           annouce_time=annouce_time, start_time=start_time, finish_time=finish_time,
                                           lessoninfo=lessoninfo, certificate=certificate, address=address)
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


# 課程編輯清單
@login_required
def edit_lesson_list(request):
    context = {}
    # 調閱資料
    if request.user.is_staff:
        table = _get_teacher_lesson()
    else:
        table = _get_teacher_lesson(request.user.id)

    context["class_table"] = table
    return render(request, "lesson/edit_lesson/lesson_table.html", context)


# 課程編輯頁面
@login_required
def edit_lesson(request):
    return render(request, "lesson/edit_lesson/edit_lesson_page.html")


# 課程編輯子頁面載入
def lesson_edit_page(request):
    template = "lesson/edit_lesson/"
    request_page = request.GET.get("page", "")
    lessonid = request.GET.get("lessonid", "")
    info = models.Lesson.objects.get(lessonid=lessonid)
    media = models.Multimedia.objects.filter(lesson_id_id=lessonid)
    student = models.Studentlist.objects.filter(lesson_id_id=lessonid)
    lesson_table = models.LessonTable.objects.filter(lesson_id_id=lessonid)

    context = {"info": info, "media": media, "student": student,
               "lesson_table": lesson_table, "today": datetime.today()}
    if request_page == "basic_info":
        html = "basic_info.html"
    elif request_page == "class_list":
        html = "class_list.html"
    elif request_page == "student_list":
        html = "student_list.html"
    elif request_page == "homework":
        html = "homework.html"
    else:
        html = "test.html"

    return render(request, template + html, context)


# 課程編輯儲存
def lesson_edit_save(request):

    return render(request)


# 刪除課程
@login_required
def delete_lesson(request):
    context = {}
    lesson_id = int(request.GET.get('lessonid'))
    try:
        models.Lesson.objects.get(lessonid=lesson_id).delete()
        context['result'] = True
    except:
        context['result'] = False
    return JsonResponse(context)


# 參加課程畫面
@login_required
def joinorquit(request):
    context = {}
    # 資料調閱
    lessoninfo = models.Lesson.objects.get(lessonid=int(request.GET.get('lessonid')))
    in_class = _already_in_lesson(int(request.user.id), int(request.GET.get('lessonid')))

    # 整理相關情報
    context["in_class"] = in_class
    situation = lessoninfo.situation
    context["situation"] = situation
    context["lessonid"] = lessoninfo.lessonid

    return render(request, "lesson/joinorquit.html", context)


# 參加課程
def join_lesson(request):
    context = {}
    situation = request.GET.get('situation')

    # 檢查重複參加問題
    in_class = _already_in_lesson(int(request.user.id), int(request.GET.get('lessonid')))
    if in_class:
        context['msg'] = 'alreadyin'
        return JsonResponse(context)
    else:
        # 線上
        if situation == 'online':
            models.Studentlist.objects.create(student_id=request.user.id, lesson_id_id=int(request.GET.get('lessonid')),
                                              first_name=request.user.first_name, last_name=request.user.last_name,
                                              lesson_situation='online')
            context['msg'] = "已參加線上課程"
        # 實體
        elif situation == 'entity':
            models.Studentlist.objects.create(student_id=request.user.id, lesson_id_id=int(request.GET.get('lessonid')),
                                              first_name=request.user.first_name, last_name=request.user.last_name,
                                              lesson_situation='entity')
            context['msg'] = "已參加實體課程"
        return JsonResponse(context)


# 退出課程
def quit_lesson(request):
    context = {}
    try:
        models.Studentlist.objects.get(student_id=request.user.id, lesson_id_id=int(request.GET.get('lessonid'))).delete()
        context['msg'] = '退出成功'
        context["situation"] = models.Lesson.objects.get(lessonid=int(request.GET.get('lessonid'))).situation
    except models.Studentlist.DoesNotExist:
        context['msg'] = '系統錯誤'
    return JsonResponse(context)


# inner function
def _get_teacher_lesson(userid: str = 0):
    if userid != 0:
        query = models.Lesson.objects.filter(auth=userid)
    else:
        query = models.Lesson.objects.all()

    result = read_frame(query)

    # 翻譯資料
    result.loc[result["situation"] == "online", "situation"] = "線上"
    result.loc[result["situation"] == "entity", "situation"] = "實體"
    result.loc[result["situation"] == "both", "situation"] = "並行"

    result.loc[result["address"] == "online mode", "address"] = "線上課程，無地址"

    return result


def _already_in_lesson(student_id: int, lesson_id: int):
    try:
        query = models.Studentlist.objects.get(student_id=student_id, lesson_id_id=lesson_id)
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
