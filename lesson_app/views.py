from django.shortcuts import render
from django.template.defaulttags import register
from django.http import JsonResponse, Http404
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django_pandas.io import read_frame
import pandas as pd
import numpy as np
from distutils.util import strtobool
from datetime import datetime
from lesson_app import models
from lesson_app import public_api


# 課程表
def callesson(request):
    if int(request.GET.get("more", "0")):
        lesson_result = models.Lesson.objects.all().order_by('-annouce_time')
    else:
        # 查詢最新10筆資料
        lesson_result = models.Lesson.objects.all().order_by('-annouce_time')[:10]

    context = {'result_table': lesson_result}
    return render(request, "common/lesson.html", context)


# 讀取封面
@register.filter
def cover_id(item, lid):
    # 嘗試找尋
    try:
        return models.Multimedia.objects.get(lesson_id_id=lid, cover=1).image.url
    # 找不到 載入預設圖片
    except models.Multimedia.DoesNotExist:
        return "static/element/empty_lesson_image.jpg"


# 首頁存取
def for_index_page():
    # 取得資最新課程資料
    lesson_result = models.Lesson.objects.all().order_by('-annouce_time')[:6]
    lesson_id_list = [item.lessonid for item in lesson_result.all()]

    # 找尋對應封面照
    cover = models.Multimedia.objects.filter(lesson_id__in=lesson_id_list, cover=1)

    return lesson_result, cover


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
    try:
        teacher = auth.models.User.objects.get(id=info.auth)
    except Exception as e:
        print(e)
        teacher = {"last_name": "unknow"}

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
        authid = request.user.id
        situation = request.POST.get('lesson_mode', '')
        verify = strtobool(request.POST.get('verify', ''))
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
        new = models.Lesson.objects.create(name=name, lessontype=lessontype, auth=authid, situation=situation,
                                           verify=verify, annouce_time=annouce_time,
                                           start_time=start_time, finish_time=finish_time,
                                           lessoninfo=lessoninfo, certificate=certificate, address=address)
        new.save()
        # 課程表資料輸入
        for i in range(lesson_table.shape[0]):
            models.LessonTable.objects.create(lesson_id_id=new.lessonid,
                                              ch=int(lesson_table["chapter"][i]),
                                              sb=int(lesson_table["submit"][i]),
                                              title=lesson_table["title"][i])
        # 課程封面輸入
        if 'cover' in request.FILES:
            models.Multimedia.objects.create(lesson_id_id=new.lessonid, cover=1, media_type=1,
                                             image=request.FILES['cover'], filename=request.FILES['cover'].name)

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
    # 查無參數
    if "lessonid" not in request.GET:
        raise Http404
    else:
        return render(request, "lesson/edit_lesson/edit_lesson_page.html")


# 課程編輯子頁面載入
@login_required
def lesson_edit_page(request):
    template = "lesson/edit_lesson/"
    request_page = request.GET.get("page", "")
    lessonid = request.GET.get("lessonid", "")
    info = models.Lesson.objects.get(lessonid=lessonid)
    media = read_frame(models.Multimedia.objects.filter(lesson_id_id=lessonid))
    cover = read_frame(models.Multimedia.objects.filter(lesson_id_id=lessonid, cover=1))
    student = read_frame(models.Studentlist.objects.filter(lesson_id_id=lessonid))
    lesson_table = read_frame(models.LessonTable.objects.filter(lesson_id_id=lessonid))
    lesson_table = lesson_table.sort_values(by=['ch', 'sb'])

    context = {"info": info, "media": media, "student": student, "cover": cover,
               "lesson_table": lesson_table, "today": datetime.today()}

    # 載入基本資料
    if request_page == "basic_info":
        html = "basic_info.html"

    # 載入課綱資料
    elif request_page == "class_list":
        context["lesson_count"] = lesson_table.shape[0]
        context["lesson_id_count"] = lesson_table.shape[0] - 1
        context["media_info"] = models.LessonRelatedMedia.objects.filter(lesson_id=lessonid)
        html = "course_outline.html"

    # 載入學生清單
    elif request_page == "student_list":
        # 調閱使用者詳細資料
        join_student = student["student_id"].to_list()
        from users.models import UesrInfo
        userinfo = read_frame(UesrInfo.objects.filter(id__in=join_student)
                              .values('id', 'username', 'address', 'email', 'telephone', 'region'))

        # merge
        context["student"] = pd.merge(context["student"], userinfo, left_on='student_id', right_on='id')

        # 翻譯資料
        context["student"].loc[context["student"]["lesson_situation"] == "online", "lesson_situation"] = "線上"
        context["student"].loc[context["student"]["lesson_situation"] == "entity", "lesson_situation"] = "實體"
        context["student"].loc[context["student"]["lesson_situation"] == "both", "lesson_situation"] = "並行"
        html = "student_list.html"

    # 習題管理
    elif request_page == "homework":
        homework_info = models.Homework.objects.filter(lesson_id_id=lessonid)
        hwid = [item.inner_id for item in homework_info.all()]
        homework_attach = models.HomeworkAttachFile.objects.filter(homeworkid_id__in=hwid)
        context["homework_info"] = homework_info
        context["homework_attach"] = homework_attach
        html = "homework.html"
    else:
        html = "test.html"

    return render(request, template + html, context)


# 教師作業評分
def homework_mark(request):
    context = {}
    # 教師開課資料
    if request.user.is_staff:
        lesson = models.Lesson.objects.all()
        subject = models.LessonTable.objects.all()
    else:
        lesson = models.Lesson.objects.filter(auth=request.user.id)
        lessonid = [item.lessonid for item in lesson.all()]
        subject = models.LessonTable.objects.filter(lesson_id_id__in=lessonid)

    return render(request, "lesson/handout_homework/homework_mark_index.html", context)


# 刪除作業
@login_required
def delete_homework(request):
    context = {}
    homeworkid = int(request.GET.get("homeworkid", ""))
    try:
        target = models.Homework.objects.get(inner_id=homeworkid)
        target.delete()
        context["result"] = True
    except Exception as e:
        print(e.__doc__)
        context["result"] = False

    return JsonResponse(context)


# 刪除課程
@login_required
def delete_lesson(request):
    context = {}
    lesson_id = int(request.GET.get('lessonid'))
    try:
        models.Lesson.objects.get(lessonid=lesson_id).delete()
        context['result'] = True
    except Exception as e:
        print(e.__doc__)
        context['result'] = False
    return JsonResponse(context)


# 參加課程畫面
@login_required
def joinorquit(request):
    context = {}
    # 資料調閱
    lessoninfo = models.Lesson.objects.get(lessonid=int(request.GET.get('lessonid')))
    in_class = public_api.already_in_lesson(int(request.user.id), int(request.GET.get('lessonid')))

    # 整理相關情報
    context["in_class"] = in_class
    context["lessoninfo"] = lessoninfo

    return render(request, "lesson/joinorquit.html", context)


# 參加訂閱課程清單
@login_required
def join_lesson_list(request):
    context = {}
    # 已加入課程清單
    join_list = models.Studentlist.objects.filter(student_id=request.user.id)

    # 加入課程資料解析
    columns = [fields.name for fields in models.Lesson._meta.get_fields(include_hidden=False)]
    lesson = pd.DataFrame(columns=columns)
    for data in join_list:
        dict_data = pd.DataFrame(data.lesson_id.to_dict(), index=[0])
        lesson = lesson.append(dict_data)

    # 開課人資料調閱
    teacher = read_frame(auth.models.User.objects.filter(id__in=lesson["auth"].to_list()))
    teacher = teacher[['id', 'first_name', 'last_name', 'email']]
    # merge
    context["result"] = pd.merge(lesson, teacher, left_on="auth", right_on="id")

    # 翻譯資料

    return render(request, "lesson/join_lesson_list.html", context)


# 上課
@login_required
def class_room(request):
    context = {}
    try:
        # get data
        lessonid = request.GET.get("lessonid", "")
        lesson_table_inner_id = request.GET.get("t_id", -1)
        context["inner_id"] = int(lesson_table_inner_id)

        # 調閱課程資料
        context["lesson_info"] = models.Lesson.objects.get(lessonid=lessonid)

        # 調閱課綱
        lesson_table = models.LessonTable.objects.filter(lesson_id_id=lessonid)
        context["lesson_table"] = read_frame(lesson_table).sort_values(by=['ch', 'sb'])

        # 調閱課程資訊
        # 教材抓取
        lesson_media = models.LessonRelatedMedia.objects.filter(t_id_id=lesson_table_inner_id)
        context["lesson_media"] = lesson_media

        # 作業資訊抓取
        homework_info = models.Homework.objects.filter(lessontable_id=lesson_table_inner_id)
        context["homework_info"] = homework_info

    except models.Lesson.DoesNotExist:
        raise Http404

    return render(request, "lesson/class_room/class_room.html", context)


# 調閱可繳交作業
@login_required
def handout_homework(request):
    context = {}
    # 抓取資料
    if request.method.lower() == "get":
        lessonid = request.GET.get("lessonid", -1)
        homework_data = models.Homework.objects.filter(lesson_id=lessonid).\
            order_by("lessontable_id__ch", "lessontable_id__sb")
        context["lessonid"] = lessonid
        context["homework_data"] = homework_data
    return render(request, "lesson/handout_homework/homework_index.html", context)


@register.filter
def hw_attach_file(item, hwid):
    return models.HomeworkAttachFile.objects.filter(homeworkid_id=hwid)


@register.filter
def hw_submit_info(user_id, hwid):
    query = models.HomeworkSubmit.objects.filter(user_id=user_id, homework_id_id=hwid)
    if len(query) > 0:
        return query
    else:
        return {None}


@register.filter
def hw_submit_file(empty, hwsubmit_id):
    if type(hwsubmit_id) is int:
        return models.HomeworkFileTable.objects.filter(homeworksubmit_id_id=hwsubmit_id)


@register.filter
def hw_hand_in(user_id, hwid):
    try:
        query = models.HomeworkSubmit.objects.get(user_id=user_id, homework_id_id=hwid)
        return True
    except models.HomeworkSubmit.DoesNotExist:
        return False


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


def _creat_lesson_table(requese, size, count_str, update: bool = False):
    # 判斷為建立新課程與否
    if update is False:
        df = pd.DataFrame(columns=['chapter', 'submit', 'title'])
        for i in range(count_str + 1):
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
    else:
        df = pd.DataFrame(columns=['inner_id', 'chapter', 'submit', 'title'])
        for i in range(count_str+1):
            inner_id_index = 'inner' + str(i)
            ch_index = 'ch' + str(i)
            sb_index = 'sb' + str(i)
            title_index = 'title' + str(i)

            if requese.POST.get(ch_index) is not None:
                # 新增項目 id設置為0
                if requese.POST.get(inner_id_index) is None:
                    inner_id = 0
                else:
                    inner_id = requese.POST.get(inner_id_index)

                if requese.POST.get(ch_index) == "":
                    ch = 0
                else:
                    ch = requese.POST.get(ch_index)

                if requese.POST.get(sb_index) == "":
                    sb = 0
                else:
                    sb = requese.POST.get(sb_index)

                title = requese.POST.get(title_index)
                df = df.append({'inner_id': inner_id, 'chapter': ch, 'submit': sb, 'title': title}, ignore_index=True)

    # 重新排列
    df = df.sort_values(by=['chapter', 'submit'])
    return df


# 檔案清單
def _creat_file_table(request):
    df = pd.DataFrame(columns=["lesson_table_inner_id", "FILE", "newfile", "deletefile"])

    # 應對新增檔案
    # 抽取新增檔案key
    key = list(request.FILES.keys())

    for i in range(len(key)):
        df = df.append({"lesson_table_inner_id": request.POST.get(key[i] + "_lesson_table_id"),
                        "FILE": request.FILES.get(key[i]), "newfile": True, "deletefile": False}, ignore_index=True)

    # 應對刪除檔案
    lessonid = request.POST.get("lessonid", "")
    file_list = models.Multimedia.objects.filter(lesson_id_id=lessonid, cover=False)

    for item in file_list.all():
        name = "remove_%d" % item.media_id
        related1 = models.LessonRelatedMedia.objects.get(media_id=item.media_id)
        if strtobool(request.POST.get(name)):
            df = df.append({"lesson_table_inner_id": related1.t_id_id,
                            "FILE": related1.media_id.file, "newfile": False, "deletefile": True}, ignore_index=True)
    return df


# Django's range
@register.filter
def d_range(v):
    return range(v)
