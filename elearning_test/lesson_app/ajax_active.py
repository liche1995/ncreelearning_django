from distutils.util import strtobool
import pandas as pd
import numpy as np
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django_pandas.io import read_frame
from lesson_app import models
from lesson_app import public_api


# 參加課程
@login_required
def join_lesson(request):
    context = {}
    situation = request.GET.get('situation')

    # 檢查重複參加問題
    in_class = public_api.already_in_lesson(int(request.user.id), int(request.GET.get('lessonid')))
    if in_class:
        context['msg'] = '先前已參加本課程'
        return JsonResponse(context)
    else:
        lessoninfo = models.Lesson.objects.get(lessonid=int(request.GET.get('lessonid')))
        if lessoninfo.verify:
            agree = False
        else:
            agree = True
        # 線上
        if situation == 'online':
            models.Studentlist.objects.create(student_id=request.user.id, lesson_id_id=int(request.GET.get('lessonid')),
                                              first_name=request.user.first_name, last_name=request.user.last_name,
                                              lesson_situation='online', agree=agree)
            context['msg'] = "已參加線上課程"
        # 實體
        elif situation == 'entity':
            models.Studentlist.objects.create(student_id=request.user.id, lesson_id_id=int(request.GET.get('lessonid')),
                                              first_name=request.user.first_name, last_name=request.user.last_name,
                                              lesson_situation='entity', agree=agree)
            context['msg'] = "已參加實體課程"
        return JsonResponse(context)


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


# 繳交作業編輯
@login_required
def homework_submit_edit_save(request):
    context = {}
    # 禁制非post操作
    if request.method.lower() == "post":
        lessonid = int(request.POST.get("lessonid", ""))
        homeworkid = int(request.POST.get("homeworkid", ""))
        lesson_table_id = int(request.POST.get("lesson_table_id", ""))
        textraea = request.POST.get("textraea", "")
        already_submit = public_api.already_submit_hw(request.user.id, homeworkid)

        # 新建
        if already_submit is False:
            submitinfo_db = models.HomeworkSubmit.objects.create(lessontable_id_id=lesson_table_id, lesson_id_id=lessonid,
                                                                 homework_id_id=homeworkid, user_id=request.user.id,
                                                                 submitinfo=textraea, attach_file_exist=False)

        # 更新
        else:
            submitinfo_db = models.HomeworkSubmit.objects.get(user_id=request.user.id, homework_id_id=homeworkid)
            submitinfo_db.submitinfo = textraea

        # 增加檔案
        # 抽取key
        file_key_list = list(request.FILES.keys())

        for file_key in file_key_list:
            file = request.FILES.get(file_key)
            models.HomeworkFileTable.objects.create(file=file,
                                                    homeworksubmit_id_id=submitinfo_db.inner_id,
                                                    lesson_id_id=lessonid, lessontable_id_id=lesson_table_id)

        # 刪除檔案
        # 抽取key
        delete_key = np.array(list(request.POST.keys()))
        delete_key_index = np.where(np.char.find(delete_key, "delete_") == 0)[0]
        for i in delete_key_index:
            delete_order = request.POST.get(delete_key[i])
            # 要求刪除
            if strtobool(delete_order):
                inner_id = int(delete_key[i].split("_")[-1])
                models.HomeworkFileTable.objects.get(inner_id=inner_id).delete()

        # 附檔有無最後檢查
        if len(models.HomeworkFileTable.objects.filter(homeworksubmit_id=submitinfo_db.inner_id)) > 0:
            submitinfo_db.attach_file_exist = True
        else:
            submitinfo_db.attach_file_exist = False

        submitinfo_db.save()

        context["msg"] = "上傳成功"

    # 非POST request
    else:
        context["msg"] = "系統錯誤!"

    return JsonResponse(context)


# 刪除作業
def student_delete_homework(request):
    context = {}
    if request.method.lower() == "post":
        homeworkid = int(request.POST.get("homeworkid", ""))
        already_submit = public_api.already_submit_hw(request.user.id, homeworkid)

        if already_submit:
            taget = models.HomeworkSubmit.objects.get(user_id=request.user.id, homework_id_id=homeworkid)
            taget.delete()
            context["msg"] = "已刪除"

        else:
            context["msg"] = "作業不存在"

    return JsonResponse(context)


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
        cover = request.FILES.get("cover", None)
        remove_cover = bool(strtobool(request.POST.get("remove_cover", "")))

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

        # 更新封面
        if cover is not None and remove_cover is False:
            # 純更新封面
            try:
                cover_models = models.Multimedia.objects.get(lesson_id_id=lessonid, cover=1, media_type=1)
                cover_models.image = cover
                cover_models.filename = cover.name
                cover_models.save()
                context["msg"] = "完成更新"
            # 補加封面
            except models.Multimedia.DoesNotExist:
                models.Multimedia.objects.create(lesson_id_id=lessonid, cover=1, media_type=1,
                                                 image=request.FILES['cover'], filename=request.FILES['cover'].name)
                context["msg"] = "完成更新"
            # 其他例外錯誤
            except Exception as e:
                print(e.__str__)
                context["msg"] = "發生錯誤，請聯絡網站管理人員"
        # 移除封面
        elif remove_cover:
            models.Multimedia.objects.get(lesson_id_id=lessonid, cover=1, media_type=1).delete()
            context["msg"] = "完成更新"
        else:
            context["msg"] = "完成更新"

    return JsonResponse(context)


# 課綱編輯儲存
@login_required
def course_outline_edit_save(request):
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

        # 移除課綱
        old_inner_id = old_lesson_table["inner_id"].to_numpy()
        old_inner_id = old_inner_id.astype(int)
        new_inner_id = new_lesson_table["inner_id"].to_numpy()
        new_inner_id = new_inner_id.astype(int)
        remove_target = np.setdiff1d(old_inner_id, new_inner_id)
        for i in range(remove_target.shape[0]):
            models.LessonTable.objects.get(inner_id=remove_target[i]).delete()

        # 更新、新增課綱
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

        # 產生檔案操作清單
        file_table = _creat_file_table(request)

        # 新增或移除檔案
        for file_list in file_table.iloc:
            # 新增檔案
            if file_list.newfile:
                # 媒體表新增資料
                new_media = models.Multimedia.objects.create(lesson_id_id=lessonid, cover=False, textbook=True,
                                                             media_type=0, file=file_list["FILE"],
                                                             filename=file_list["FILE"].name)
                # 教材連接表新增資料
                models.LessonRelatedMedia.objects.create(lesson_id=lessonid,
                                                         t_id_id=int(file_list["lesson_table_inner_id"]),
                                                         media_id_id=new_media.media_id)

            # 移除檔案
            elif file_list.deletefile:
                # 註銷資料
                models.Multimedia.objects.get(file=file_list.FILE).delete()
            # 特殊狀況
            else:
                pass

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


# 教師作業操作
@login_required
def homework_active(request):
    context = {}
    # 禁止get方法操作
    if request.method.lower() == "get":
        context["msg"] = "系統錯誤"
    # 新增資料
    elif request.method.lower() == "post" and "homeworkid" not in request.POST:
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
            models.Homework.objects.create(lessontable_id_id=lessontable_id, title=name, homeworkinfo=homeworkinfo,
                                           attach_file_exist=attach, lesson_id_id=lessonid,
                                           finish_time=finish_date, start_time=start_date, turn_it_available=turn_it)

            # 附檔應對

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
            # 抽取作業資料
            db = models.Homework.objects.get(inner_id=homeworkid)
            db.lessontable_id_id = lessontable_id
            db.name = name
            db.lessonid = lessonid
            db.turn_it_available = turn_it
            db.start_date = start_date
            db.finish_date = finish_date
            db.homeworkinfo = homeworkinfo

            db.attach_file_exist = attach

            # 附檔應對
            # 抽取附檔資料
            try:
                file_db = models.HomeworkAttachFile.objects.get(homeworkid=homeworkid)
            except models.HomeworkAttachFile.DoesNotExist:
                file_db = None
            file = request.FILES.get("attach_file", "")

            # 追加
            if attach == 1 and file != "" and file_db is None:
                models.HomeworkAttachFile.objects.create(homeworkid_id=homeworkid, file=file)

            # 抽換
            if attach == 1 and file != "" and file_db is not None and file_db.filename() != file.name:
                # 刪除原本檔案
                file_db.delete()
                # 重新增加檔案
                models.HomeworkAttachFile.objects.create(homeworkid_id=homeworkid, file=file)

            # 刪除
            if attach == 0 and file_db is not None:
                file_db.delete()

            # 收尾，回傳成果
            db.save()
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
