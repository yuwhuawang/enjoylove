#coding:utf-8
from django.conf.urls import include, url
from views import (user_login, user_register, verify_sms_code, gen_sms_code,
                   forgot_password, reset_password,
                   test, upload_avatar, set_gender, verify_identity, set_basic_info,
                   get_user_tags, set_user_tags, user_init, user_album, set_album,
                   delete_album, user_contact, set_contact, person_list)
urlpatterns = [
    url(r'^init', user_init),
    url(r'^login', user_login),
    url(r'^register', user_register),
    url(r'^verify-sms-code', verify_sms_code),
    url(r'^gen-sms-code', gen_sms_code),
    url(r'^reset/password', reset_password),
    url(r'^forgot/password', forgot_password),
    url(r'^test/', test),
    url(r'^set/avatar', upload_avatar),
    url(r'^set/gender', set_gender),
    url(r'^verify/identity', verify_identity),
    url(r'^set/basic-info', set_basic_info),
    url(r'^tags', get_user_tags),
    url(r'^set/tags', set_user_tags),
    url(r'^albums/', user_album),
    url(r'^set/album/', set_album),
    url(r'^delete/albums', delete_album),
    url(r'^contacts', user_contact),
    url(r'^set/contact', set_contact),
    url(r'^persons', person_list)
]