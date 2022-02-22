from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from lesson_app import models as lesson_models
from . import models as rollcall_models
import datetime


# Create your views here.
@login_required
def view_init(request):
    context = {}
    if request.user.is_staff:
        lesson_info = lesson_models.Lesson.objects.all()
    else:
        lesson_info = lesson_models.Lesson.objects.filter(auth=request.user.id)
    context["lesson_info"] = lesson_info
    return render(request, "rollcall/info.html", context)


def lesson_sub_info(request):
    context = {}
    context["lessonid"] = int(request.GET.get("lessonid", ""))
    context["subject_lesson"] = lesson_models.LessonTable.objects.filter(lesson_id_id=context["lessonid"])
    return render(request, "rollcall/sub_info.html", context)


def call_table(request):
    context = {}
    subject_id = request.GET.get("subject_id", -9)

    subject_object = lesson_models.LessonTable.objects.get(inner_id=int(subject_id))

    order = "select * from lesson_studentlist as s " \
            "left outer join lesson_table as lt " \
            "on s.lesson_id_id = lt.lesson_id_id " \
            "left outer join rollcall as r " \
            "on r.user_id = s.student_id and r.lessontableid_id = lt.inner_id " \
            "where lt.inner_id = " + subject_id

    context["rollcall"] = rollcall_models.Rollcall.objects.raw(order)
    context["subject_id"] = subject_id
    return render(request, "rollcall/table.html", context)


def submit_rollcall(request):
    context = {}
    context["msg"] = "發生錯誤"
    # 抓取資料
    if request.method.lower() != 'post':
        context["msg"] = "發生錯誤"
    else:
        rollcall_time = request.POST.getlist("manual_rollcall_time", [])
        student_list = request.POST.getlist("student_id", [])
        subject_id = int(request.POST.get("subject_id", ""))
        enable_manual = request.POST.getlist("manual_enable", [])

        # 合併資料

        rollcall_table = [
            [int(student_list[i]), float(rollcall_time[i] if rollcall_time[i] != "" else 0), enable_manual[i]]
            for i in range(len(student_list))]

        # 新增或更新
        for student in rollcall_table:
            if student[3]:
                try:
                    info = rollcall_models.Rollcall.objects.get(user_id=student[0])
                    info.sign_in_time = datetime.datetime.fromtimestamp(student[1])
                    info.save()
                except rollcall_models.Rollcall.DoesNotExist:
                    rollcall_models.Rollcall.objects.create(
                        lessontableid_id=subject_id, user_id=student[0], sign_in_time=datetime.datetime.fromtimestamp(student[1]))
            else:
                continue

        context["msg"] = "完成上傳"

    return JsonResponse(context)
