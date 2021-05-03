from django.shortcuts import render
from django.template.defaulttags import register
from django.http import JsonResponse, Http404
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django_pandas.io import read_frame
from rest_framework.decorators import api_view
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
        new = models.Lesson.objects.create(name=name, lessontype=lessontype, auth=auth, situation=situation, verify=verify,
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
        if 'cover' in request.FILES:
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
    student = read_frame(models.Studentlist.objects.filter(lesson_id_id=lessonid))
    lesson_table = read_frame(models.LessonTable.objects.filter(lesson_id_id=lessonid))
    lesson_table = lesson_table.sort_values(by=['ch', 'sb'])

    context = {"info": info, "media": media, "student": student,
               "lesson_table": lesson_table, "today": datetime.today()}
    if request_page == "basic_info":
        html = "basic_info.html"
    elif request_page == "class_list":
        context["lesson_count"] = lesson_table.shape[0]
        context["lesson_id_count"] = lesson_table.shape[0] - 1
        html = "class_list.html"
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
    elif request_page == "homework":
        homework_info = models.Homework.objects.filter(lesson_id_id=lessonid)

        # merge
        homework_info = pd.merge(read_frame(homework_info), lesson_table,
                                 left_on="lessontable_id", right_on="inner_id", how="left",
                                 suffixes=["_hw", "_lt"])
        # 無章節修飾
        homework_info.loc[homework_info["ch"].isnull(), "ch"] = 0
        homework_info.loc[homework_info["sb"].isnull(), "sb"] = 0
        homework_info.loc[homework_info["title_lt"].isnull(), "title_lt"] = "未指定章節"
        homework_info["inner_id_lt"] = homework_info["lessontable_id"]

        change_columns = np.where(homework_info.dtypes == np.float64)
        change_columns_name = homework_info.columns[change_columns].to_list()
        homework_info[change_columns_name] = homework_info[change_columns_name].astype(int)

        # sort
        homework_info = homework_info.sort_values(by=["ch", "sb", "title_hw"])

        context["homework_info"] = homework_info
        html = "homework.html"
    else:
        html = "test.html"

    return render(request, template + html, context)


# 課程編輯儲存
@login_required
def lesson_edit_save(request):
    context = {}
    # 禁制非post操作
    if request.method.lower() != 'post':
        context["msg"] = "系統錯誤!"
    else:
        # 抓取資料
        lessonid = request.POST.get('lessonid', '')
        name = request.POST.get('lessoname', '')
        lessontype = request.POST.get('lessontype', '')
        situation = request.POST.get('lesson_mode', '')
        verify = strtobool(request.POST.get('verify', ''))
        start_time = request.POST.get('start_time', '')
        finish_time = request.POST.get('finish_time', '')
        lessoninfo = request.POST.get('lessoninfo', '')
        certificate = strtobool(request.POST.get('sing_licnese', ''))
        address = request.POST.get('address', 'online mode')

        # 存取資料庫
        info = models.Lesson.objects.get(lessonid=lessonid)
        info.name = name
        info.lessontype = lessontype
        info.situation = situation
        info.verify = verify
        info.start_time = start_time
        info.finish_time = finish_time
        info.lessoninfo = lessoninfo
        info.certificate = certificate
        info.address = address
        info.save()
        context["msg"] = "完成更新"
    return JsonResponse(context)


# 課綱編輯儲存
@login_required
def lesson_table_edit_save(request):
    context = {}
    # 禁制非post操作
    if request.method.lower() != "post":
        context["msg"] = "系統錯誤!"
    else:
        lessonid = request.POST.get("lessonid", "")
        # 取得原始課表
        old_lesson_table = read_frame(models.LessonTable.objects.filter(lesson_id_id=lessonid))

        # 動態變化資料
        lesson_count = int(request.POST.get("lesson_count", ""))
        lesson_id_count = int(request.POST.get("lesson_id_count", ""))

        # 產生新課表
        new_lesson_table = _creat_lesson_table(request, lesson_count, lesson_id_count, True)

        # 移除
        old_inner_id = old_lesson_table["inner_id"].to_numpy()
        old_inner_id = old_inner_id.astype(int)
        new_inner_id = new_lesson_table["inner_id"].to_numpy()
        new_inner_id = new_inner_id.astype(int)
        remove_target = np.setdiff1d(old_inner_id, new_inner_id)
        for i in range(remove_target.shape[0]):
            models.LessonTable.objects.get(inner_id=remove_target[i]).delete()

        # 更新、新增
        for i in range(new_lesson_table.shape[0]):
            # 更新
            if new_lesson_table["inner_id"][i] != 0:
                update = models.LessonTable.objects.get(inner_id=new_lesson_table["inner_id"][i])
                update.ch = new_lesson_table["chapter"][i]
                update.sb = new_lesson_table["submit"][i]
                update.title = new_lesson_table["title"][i]
                update.save()
            # 新增
            else:
                models.LessonTable.objects.create(lesson_id_id=lessonid,
                                                  ch=int(new_lesson_table["chapter"][i]),
                                                  sb=int(new_lesson_table["submit"][i]),
                                                  title=new_lesson_table["title"][i])

        context["msg"] = "完成更新"
    return JsonResponse(context)


# 學生清單操作
@login_required
def student_manage(request):
    context = {}
    decide = request.GET.get("decide", "")
    student_id = request.GET.get("student_id", "")
    lessonid = request.GET.get("lessonid", "")
    # 拒絕參加
    if decide == "denied" and student_id != "" and lessonid != "":
        student_lesson_info = models.Studentlist.objects.get(student_id=student_id, lesson_id_id=lessonid)
        student_lesson_info.agree = False
        student_lesson_info.save()

        context["msg"] = "已拒絕參加"
        context["system"] = True

    # 允許參加
    elif decide == "agree" and student_id != "" and lessonid != "":
        student_lesson_info = models.Studentlist.objects.get(student_id=student_id, lesson_id_id=lessonid)
        student_lesson_info.agree = True
        student_lesson_info.save()

        context["msg"] = "已允許參加"
        context["system"] = True

    # 特殊狀況
    else:
        context["msg"] = "系統錯誤"
        context["system"] = False

    return JsonResponse(context)


# 作業操作
@login_required
def homework_active(request):
    context = {}
    # 抓取資料
    if request.method.lower() == "get":
        pass
    # 新增資料
    elif request.method.lower() == "post" and "homeworkid" in request.POST is False:
        # 整理表單資料
        lessontable_id = int(request.POST.get("lessontable_id", ""))
        name = request.POST.get("name", "")
        attach = strtobool(request.POST.get("attach", ""))
        lessonid = int(request.POST.get("lessonid", ""))
        turn_it = strtobool(request.POST.get("turn_it", ""))
        start_date = request.POST.get("start_date", "")
        finish_date = request.POST.get("finish_date", "")
        homeworkinfo = request.POST.get("homeworkinfo", "")

        # 輸入資料庫
        try:
            db = models.Homework.objects.create(lessontable_id=lessontable_id, title=name, homeworkinfo=homeworkinfo,
                                                attach_file_exist=attach, lesson_id_id=lessonid, finish_time=finish_date,
                                                start_time=start_date, turn_it_available=turn_it)

            # 回傳成果
            context["msg"] = "新增成功"

        except Exception as e:
            print(e.__doc__)
            context["msg"] = "系統錯誤"
    # 更新作業資料
    elif request.method.lower() == "post" and "homeworkid" in request.POST:
        # 整理表單資料
        homeworkid = int(request.POST.get("homeworkid", ""))
        lessontable_id = int(request.POST.get("lessontable_id", ""))
        name = request.POST.get("name", "")
        attach = strtobool(request.POST.get("attach", ""))
        lessonid = int(request.POST.get("lessonid", ""))
        turn_it = strtobool(request.POST.get("turn_it", ""))
        start_date = request.POST.get("start_date", "")
        finish_date = request.POST.get("finish_date", "")
        homeworkinfo = request.POST.get("homeworkinfo", "")

        # 輸入資料庫
        try:
            db = models.Homework.objects.get(inner_id=homeworkid)
            db.lessontable_id = lessontable_id
            db.name = name
            db.attach = attach
            db.lessonid = lessonid
            db.turn_it_available = turn_it
            db.start_date = start_date
            db.finish_date = finish_date
            db.homeworkinfo = homeworkinfo
            db.save()

            # 回傳成果
            context["msg"] = "更新成功"

        except Exception as e:
            print(e.__doc__)
            context["msg"] = "系統錯誤"

    return JsonResponse(context)


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


# 刪除學生
@login_required
def kick_studnet(request):
    context = {}
    student_id = request.GET.get("student_id", "")
    lessonid = request.GET.get("lessonid", "")
    try:
        models.Studentlist.objects.get(student_id=student_id, lesson_id_id=lessonid).delete()
        # 刪除成功
        context["msg"] = "學生刪除成功"
        context["result"] = True
    except Exception as e:
        # 刪除失敗
        print(e.__doc__)
        context["msg"] = "系統錯誤，刪除失敗"
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
    in_class = _already_in_lesson(int(request.user.id), int(request.GET.get('lessonid')))

    # 整理相關情報
    context["in_class"] = in_class
    situation = lessoninfo.situation
    context["situation"] = situation
    context["lessonid"] = lessoninfo.lessonid

    return render(request, "lesson/joinorquit.html", context)


# 參加課程
@login_required
def join_lesson(request):
    context = {}
    situation = request.GET.get('situation')

    # 檢查重複參加問題
    in_class = _already_in_lesson(int(request.user.id), int(request.GET.get('lessonid')))
    if in_class:
        context['msg'] = '先前已參加本課程'
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


# 參加訂閱課程清單
@login_required
def join_lesson_list(request):
    context = {}
    # 已加入課程清單
    join_list = models.Studentlist.objects.filter(student_id=request.user.id)

    # 加入課程資料解析
    columns = [fields.name for fields in models.Lesson._meta.fields]
    lesson = pd.DataFrame(columns=columns)
    for data in join_list:
        dict_data = pd.DataFrame(data.lesson_id.to_dict(), index=[0])
        lesson = lesson.append(dict_data)

    # 開課人資料調閱
    teacher = read_frame(auth.models.User.objects.filter(id__in=lesson["auth"].to_list()))

    # merge
    context["result"] = pd.merge(lesson, teacher, left_on="auth", right_on="id")

    # 翻譯資料

    return render(request, "lesson/join_lesson_list.html", context)


# 退出課程
@login_required
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
                df = df.append({'inner_id':inner_id, 'chapter': ch, 'submit': sb, 'title': title}, ignore_index=True)

    # 重新排列
    df = df.sort_values(by=['chapter', 'submit'])
    return df


# Django's range
@register.filter
def d_range(v):
    return range(v)
