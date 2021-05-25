from django.http import HttpResponse, HttpResponseRedirect, FileResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.template.defaulttags import register
from django_pandas.io import read_frame
from lesson_app.public_api import *
from lesson_app.views import for_index_page
from lesson_app.models import Multimedia
import pandas as pd
import mimetypes

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
    # 讀取最新開課資訊
    newest_lesson_info = for_index_page()
    context['newest_lesson_info'] = newest_lesson_info

    return render(request, "common/index.html", context)


# 課程頁
def callesson(request):
    context = {}
    return render(request, "common/lesson.html", context)


# 多媒體存取權限檢查
def request_file_access(request, path, document_root):
    # 判斷格式
    filetype = mimetypes.guess_type(path)

    # 圖片存取，查無檔案 raise 404
    if "image" in filetype[0]:
        document = get_object_or_404(Multimedia, image=path)
        response = FileResponse(document.image)
    # 其他檔案存取，查無檔案 raise 404
    else:
        document = get_object_or_404(Multimedia, file=path)
        response = FileResponse(document.file)

    # 確認存取權限
    # 無限制存取
    if document.open_access:
        return response

    # 限制會員存取
    if document.open_access is False and request.user.is_authenticated:
        # 對參加人員公開
        if document.only_for_members:
            # 檢查資格
            if already_in_lesson(request.user.id, document.lesson_id_id):
                return response
            # 不允許
            else:
                raise Http404
        # 對會員公開
        elif document.only_for_members is False:
            return response
        else:
            raise Http404
    else:
        raise Http404


# 403錯誤
# 一般使用
def situation_403(request, exception):

    return


# 測試使用
def test_403(request):

    return


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
