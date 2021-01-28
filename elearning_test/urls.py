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
from django.urls import path
from django.conf.urls import handler404, handler500
from elearning_test import views as main_view
from lesson_app import views as lesson_view

core = main_view.WebCore
time_core = main_view.Clockview
attest = main_view.Attri

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_view.callindex),
    path('lesson', lesson_view.callesson),
    path('login', main_view.callogin),
    #path('', core.as_view()),
    #path('time', time_core.as_view()),
    #path('test', attest.as_view()),
]

handler404 = main_view.situation_404
handler500 = main_view.situation_500
