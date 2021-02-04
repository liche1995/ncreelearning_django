from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.contrib import auth
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


# 嘗試登入
def login(request):
    if request.user.is_authenticated:
        return render(request, 'account/login.html')
    # 抓取帳號與密碼
    username = request.POST.get('account', "")
    password = request.POST.get('password', "")
    # 啟動驗證
    context = {}
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        auth.login(request, user)
        return HttpResponseRedirect("/", context)
    else:
        context["logfail"] = True
        return render(request, "account/login.html", context)


# 註冊表單
def callsignupform(request):
    context = {}
    # 抓取帳號與密碼
    username = request.POST.get('username', "")
    password = request.POST.get('password', "")
    context["username"] = username
    context["password"] = password

    # 抓取使用條款文本
    privacy_clause_path = os.getcwd() + "\\templates\\staticfiles\\clause\\privacy_clause.txt"
    data = open(privacy_clause_path, "r")
    context["privacy_clause"] = data.read()
    data.close()
    return render(request, "account/sign_up.html", context)


# 建立使用者
def creat_user(request):
    username = request.POST.get('username', "")
    password = request.POST.get('password', "")
    last_name = request.POST.get('last_name', "")
    first_name = request.POST.get('first_name', "")
    address= request.POST.get('address', "")
    # auth.models.User.objects.create(username=)
    return render(request, "account/successed_create_account")


# 登出
def logout(request):
    auth.logout(request)
    context = {}
    return HttpResponseRedirect("/", context)


# 404錯誤
# 一般使用
def situation_404(request, exception):
    response = render(request, "common/404error.html", status=404)
    return response


# 測試使用
def test_404(request):
    return HttpResponse(status=404)


# 500錯誤
# 一般使用
def situation_500(request):
    response = render(request, "common/500error.html", status=500)
    return response


# 測試使用
def test_500(request):
    return 0


# Django's range
@register.filter
def d_range(v):
    return range(v)
