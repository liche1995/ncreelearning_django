from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib import auth
import os
from django.template.defaulttags import register
from django_pandas.io import read_frame
from users import models


# 登入頁面
def callogin(request):
    context = {}
    return render(request, "account/login.html", context)


# 嘗試登入
def login(request):
    if request.user.is_authenticated:
        return render(request, 'account/login.html')
    # 抓取帳號與密碼
    username = request.POST.get('username', "")
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


# 建立使用者
def create_user(request):
    context = {}
    # 建立註冊表單
    if len(request.POST) <= 3 or request.method == 'GET':
        return create_user_form(request)

    # 送出註冊資料
    elif len(request.POST) > 3:
        username = request.POST.get('username', "")
        password = request.POST.get('password', "")
        last_name = request.POST.get('last_name', "")
        first_name = request.POST.get('first_name', "")
        address = request.POST.get('address', "")
        email = request.POST.get('email', "")
        telephone = request.POST.get('telephone', "")
        region = request.POST.get('region', "")

        try:
            # auth models
            auth.models.User.objects.create_user(username=username, password=password,
                                                 first_name=first_name, last_name=last_name,
                                                 email=email)
            user = auth.authenticate(username=username, password=password)
            userid = user.id
            # users info
            models.UesrInfo.objects.create(id=userid, username=username, address=address, telephone=telephone,
                                    first_name=first_name, last_name=last_name, region=region,
                                    email=email)
            return render(request, "account/successed_create_account.html", context)
        except Exception as e:
            # 帳號已被建立
            if e.args[0] == 1062:
                request.session['create_error'] = 1062
                return create_user_form(request)


# 帳號申請表單
def create_user_form(request):

    context = {}
    # 抓取帳號與密碼
    username = request.POST.get('username', "")
    password = request.POST.get('password', "")
    last_name = request.POST.get('last_name', "")
    first_name = request.POST.get('first_name', "")
    address = request.POST.get('address', "")
    email = request.POST.get('email', "")
    telephone = request.POST.get('telephone', "")
    region = request.POST.get('region', "")

    context["username"] = username
    context["password"] = password
    context["last_name"] = last_name
    context["first_name"] = first_name
    context["address"] = address
    context["email"] = email
    context["telephone"] = telephone
    context["region"] = region

    # 抓取使用條款文本
    privacy_clause_path = os.getcwd() + "\\templates\\staticfiles\\clause\\privacy_clause.txt"
    data = open(privacy_clause_path, "r")
    context["privacy_clause"] = data.read()
    data.close()
    return render(request, "account/sign_up.html", context)


# 登出
def logout(request):
    auth.logout(request)
    context = {}
    return HttpResponseRedirect("/", context)


# 帳號設定頁面
def profileset(request):
    context = {}

    # 初始化
    if request.method == "GET":

        return render(request, "account/profilesetting.html", context)
    # 處理
    elif request.method == "POST":

        return render(request, "account/profilesetting.html", context)

