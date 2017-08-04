#coding:utf-8
from django.conf.urls import include, url
from views import (user_login, user_register, verify_sms_code, gen_sms_code,
                   test, upload_avatar, set_gender, verify_identity, set_basic_info,
                   init, get_user_tags, set_user_tags)
urlpatterns = [
    url(r'^init/$', init),
    url(r'^login/$', user_login),
    url(r'^register/$', user_register),
    url(r'^verify-sms-code/$', verify_sms_code),
    url(r'^gen-sms-code/$', gen_sms_code),
    url(r'^test/', test),
    url(r'^upload/avatar/', upload_avatar),
    url(r'^set/gender/', set_gender),
    url(r'^verify/identity', verify_identity),
    url(r'^set/basic-info', set_basic_info),
    url(r'^tags', get_user_tags),
    url(r'set/tags', set_user_tags)
]