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
    subject_id = int(request.GET.get("subject_id", -9))
    lessonid = int(request.GET.get("lesson_id", -9))

    if subject_id != -9:
        subject_object = lesson_models.LessonTable.objects.get(inner_id=subject_id)
        lesson_object = subject_object.lesson_id
    elif lessonid != -9:
        lesson_object = lesson_models.Lesson.objects.get(lessonid=lessonid)
    else:
        lesson_object = lesson_models.Lesson.objects.none()

    temp = lesson_models.Studentlist.objects.filter(lesson_id=lesson_object)
    return render(request, "rollcall/table.html", context)
