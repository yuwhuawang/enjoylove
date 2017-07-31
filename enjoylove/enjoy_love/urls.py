#coding:utf-8
from django.conf.urls import include, url
from django.contrib import admin
from enjoy_love.views import user_demo, user_register, verify_sms_code, gen_sms_code
urlpatterns = [
    url(r'^login/$', user_demo),
    url(r'^register/$', user_register),
    url(r'^verify_code/$', verify_sms_code),
    url(r'^gen_sms_code/$', gen_sms_code)
]