from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from lesson_app import models as lesson_models
from . import models as rollcall_models


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

    # rollcall = lesson_models.Studentlist.objects.filter(lesson_id=lesson_object)
    order = "select * from  rollcall as r " \
            "right outer join lesson_studentlist as s " \
            "on r.user_id = s.student_id " \
            "where lessontableid_id = " + subject_id + " or lesson_id_id = " + str(subject_object.lesson_id.lessonid)

    context["rollcall"] = rollcall_models.Rollcall.objects.raw(order)
    return render(request, "rollcall/table.html", context)


def submit_rollcall(request):
    context = {}
    JsonResponse(context)