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

    order = "select * from  rollcall as r " \
            "right outer join lesson_studentlist as s " \
            "on r.user_id = s.student_id " \
            "where lessontableid_id = " + subject_id + " or lesson_id_id = " + str(subject_object.lesson_id.lessonid)

    context["rollcall"] = rollcall_models.Rollcall.objects.raw(order)
    context["subject_id"] = subject_id
    return render(request, "rollcall/table.html", context)


def submit_rollcall(request):
    context = {}
    # 抓取資料
    if request.method.lower() != 'post':
        context["msg"] = False
    else:
        rollcall_time = request.POST.getlist("manual_rollcall_time", [])
        student_list = request.POST.getlist("student_id", [])
        subject_id = int(request.POST.get("subject_id", ""))

        # 合併資料

        rollcall_table = [
            [int(student_list[i]), int(rollcall_time[i] if rollcall_time[i] != "" else 0)]
            for i in range(len(student_list))]

        # 調閱、新增或更新
        for student in rollcall_table:
            try:
                info = rollcall_models.Rollcall.objects.get(user_id=student[0])
            except rollcall_models.Rollcall.DoesNotExist:
                rollcall_models.Rollcall.objects.create(
                    lessontableid_id=subject_id, user_id=student[0], sign_in_time=datetime.datetime.fromtimestamp(student[1]))

        context["msg"] = True

    return JsonResponse(context)
