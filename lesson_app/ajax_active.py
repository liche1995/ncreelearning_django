from distutils.util import strtobool
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
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
