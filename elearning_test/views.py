from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.template.defaulttags import register
import os
import time


def welcome(request):
    return HttpResponse("hello world!")


class WebCore(View):
    work_dir = os.path.abspath(os.path.dirname(os.getcwd())) + '\\elearning_test\\'

    def get(self, request):
        context = {'time': self.now_time}
        return render(request, self.work_dir+'templates\\index_.html', context)

    @staticmethod
    def now_time():
        t = time.localtime()
        result = time.strftime("%Y/%m/%d, %H:%M:%S", t)
        return result


class Clockview(View):
    work_dir = os.path.abspath(os.path.dirname(os.getcwd())) + '\\elearning_test\\'

    def get(self, request):
        w = float(request.GET['utc'])
        static_web = self.work_dir + "templates\\clock.html"
        context = {'utc': w, 'hour': int(w), 'min': 0, 'timezone': False}
        return render(request, static_web, context)


class Attri(View):
    work_dir = os.path.abspath(os.path.dirname(os.getcwd())) + '\\elearning_test\\'

    def get(self, request):
        getd = request.GET
        static_web = self.work_dir + "templates\\test.html"
        di = {"name": "闕立奇", "age": 25}
        return render(request, static_web, locals())


# 啟動首頁
def callindex(request):
    context = {}
    return render(request, "common/index.html", context)


# 課程頁
def callesson(request):
    context = {}
    return render(request, "common/lesson.html", context)


# 登入頁面
def callogin(request):
    context = {}
    return render(request, "account/login.html", context)


# Django's range
@register.filter
def d_range(v):
    return range(v)
