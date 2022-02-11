from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from lesson_app import models as lesson_models
from . import models as rollcall_models


# Create your views here.
@login_required
def view_init(request):
    context = {}
    lesson_info = lesson_models.Lesson.objects.filter(auth=request.user.id)
    context["lesson_info"] = lesson_info
    return render(request, "rollcall/info.html", context)


def lesson_sub_info(request):
    context = {}
    context["subject_lesson"] = lesson_models.LessonTable.objects.filter(lesson_id_id=int(request.GET.get("lessonid","")))
    return render(request, "rollcall/sub_info.html", context)
