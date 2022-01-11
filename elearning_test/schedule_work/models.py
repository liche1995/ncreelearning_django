from django.db import models
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from django.contrib.sessions.models import Session
import logging
from datetime import datetime

# Create your views here.

logging.basicConfig()


# 清理失效對話
def clean_expired_session():
    target_time = datetime.now().strftime("%Y-%m-%d")
    Session.objects.filter(expire_date__lte=target_time).delete()


# 註冊排程
def runtask():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    try:
        # 註冊每月初執行清理失效對話
        scheduler.add_job(clean_expired_session, 'cron', month='1-12', day='1', id='clean_expired_session',
                          replace_existing=True)

        scheduler.start()
    except Exception as e:
        print(e)
        scheduler.shutdown()
