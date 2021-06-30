"""elearning_test URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve
from django.conf import settings
from django.conf.urls import handler404, handler403, handler500
# 模組引入
from elearning_test import views as main_view
from lesson_app import views as lesson_view
from users import views as user_view
from schedule_work.models import runtask

core = main_view.WebCore
time_core = main_view.Clockview
attest = main_view.Attri
# 定時排程啟動
runtask()

urlpatterns = [
    # 基本連結設定
    path('admin/', admin.site.urls),
    path('', main_view.callindex),
    path('lesson', lesson_view.callesson),
    path('lesson_more?more=TURE', lesson_view.callesson),
    path('login_page', user_view.callogin),

    # 多媒體設定
    re_path('static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    re_path('fileinfo/(?P<path>.*)$', main_view.request_file_access, {'document_root': settings.MEDIA_ROOT}),

    # 帳號控制
    path('login', user_view.login),
    path('logout', user_view.logout),
    path('sign_up', user_view.create_user, name='sign_up'),
    path('change_password', user_view.change_password),

    # 課程操作
    path('lesson_info', lesson_view.lesson_info),

    # 登入後操作項目
    # 共通項目
    path('profileset', user_view.profileset),
    path('lesson_list', lesson_view.callesson),

    # 教師項目
    path('new_lesson', lesson_view.new_lesson),
    path('edit_lesson_list', lesson_view.edit_lesson_list),
    path('edit_lesson', lesson_view.edit_lesson),
    path('ajax_active/delete_lesson', lesson_view.delete_lesson),
    path('ajax_show/lesson_edit_page', lesson_view.lesson_edit_page),
    path('ajax_active/lesson_edit_save', lesson_view.lesson_edit_save),
    path('ajax_active/lesson_table_edit_save', lesson_view.lesson_table_edit_save),
    path('ajax_active/student_manage', lesson_view.student_manage),
    path('ajax_active/kick_studnet', lesson_view.kick_studnet),
    path('ajax_active/homework_active', lesson_view.homework_active),
    path('ajax_active/delete_homework', lesson_view.delete_homework),

    # 學生項目
    path('joinorquit_lesson', lesson_view.joinorquit),
    path("join_lesson_list", lesson_view.join_lesson_list),
    path("class_room", lesson_view.class_room),
    path("handout_homework", lesson_view.handout_homework),
    path('ajax_active/join_lesson_order', lesson_view.join_lesson),
    path('ajax_active/quit_lesson', lesson_view.quit_lesson),
    path('ajax_active/homework_submit_edit_save', lesson_view.homework_submit_edit_save),


    # 系統管理項目


    # 測試觸發
    path('test_500', main_view.test_500),
    path('test_403', main_view.test_403),
    #path('', core.as_view()),
    #path('time', time_core.as_view()),
    #path('test', attest.as_view()),
]

# 錯誤頁面指定
handler404 = main_view.situation_404
handler403 = main_view.situation_403
handler500 = main_view.situation_500
