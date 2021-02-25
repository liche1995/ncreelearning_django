from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.template.defaulttags import register
from django_pandas.io import read_frame
from users import models
import os
import re


# 登入頁面
def callogin(request):
    context = {}
    # 檢查是否為硬闖入或是Session過期
    if len(request.GET) > 0:
        context["illegal"] = True

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
    context = {}
    if request.user.is_authenticated:
        auth.logout(request)
    return HttpResponseRedirect("/", context)


# 帳號設定頁面
@login_required
def profileset(request):
    context = {}
    # 取得資料
    auth_info = request.user
    user_info = models.UesrInfo.objects.get(id=auth_info.id)

    if request.method == "GET":
        context["last_name"] = auth_info.last_name
        context["first_name"] = auth_info.first_name
        context["address"] = user_info.address
        context["email"] = auth_info.email
        context["telephone"] = user_info.telephone
        context["region"] = user_info.region.alpha3
        return render(request, "account/profilesetting.html", context)
    # 處理
    elif request.method == "POST":
        # 取得資料
        user = auth.models.User.objects.get(username=auth_info.username)

        # 修改auth資料
        user.last_name = request.POST.get("last_name", "")
        user.first_name = request.POST.get("first_name", "")
        user.email = request.POST.get("email", "")
        user.save()

        # 修改user_info資料
        user_info.telephone = request.POST.get("telephone", "")
        user_info.address = request.POST.get("address", "")
        user_info.region = request.POST.get("region", "")
        user_info.last_name = request.POST.get("last_name", "")
        user_info.first_name = request.POST.get("first_name", "")
        user_info.email = request.POST.get("email", "")
        user_info.save()
        context["change_success"] = True
        return render(request, "account/profilesetting.html", context)


# 修改密碼
@login_required
def change_password(request):
    context = {}
    if request.method == "GET":
        return render(request, 'account/change_password.html', context)
    elif request.method == "POST":
        # 檢查舊密碼
        now_password = request.user.password
        old_password = request.POST.get("oldpw")
        if check_password(old_password, now_password):
            # 檢查新密碼
            new_password = request.POST.get("newpw")
            new_password2 = request.POST.get("newpw_check")
            # 檢查格式
            if re.match("^(?=.*[a-zA-Z])(?=.*\d)[0-9a-zA-Z]{1,}$", new_password) is not None:
                # 檢查是否相符
                if new_password == new_password2:
                    auth_info = request.user
                    user = auth.models.User.objects.get(username=auth_info.username)
                    # 修改密碼
                    user.set_password(new_password)
                    user.save()
                    context["change_success"] = True
                else:
                    context["change_success"] = False
                    context["fail_resion"] = 'new_password_not_same'
            else:
                context["change_success"] = False
                context["fail_resion"] = 'new_password_format_error'
        else:
            # 舊密碼錯誤
            context["change_success"] = False
            context["fail_resion"] = 'old_password_wrong'
        # 重新渲染頁面
        return render(request, 'account/change_password.html', context)


# 權限再確認
def _recheck_password(requese):

    pass
