# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.core.cache
import django.db
import django.http
import simplejson as json
from django.contrib import auth
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from enjoy_love.util import create_verify_code
from enjoy_love.api_result import ApiResult
from django.core.cache import cache

# Create your views here.
from enjoy_love.models import User, Profile
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password
from rest_framework_jwt.settings import api_settings

from utils.sms import RestAPI as SMSSender
from django.conf import settings

def test(request):
    sms_sender = SMSSender()
    sms_sender.templateSMS(accountSid=settings.SMS_ACCOUNTSID,
                           accountToken=settings.SMS_AUTHTOKEN,
                           appId=settings.SMS_APPID,
                           toNumbers="17600369907",
                           templateId=settings.SMS_TEMPLATE_ID,
                           param="111111")

@api_view(['POST'])
@permission_classes((AllowAny,))
def user_register(request):
    username = request.POST.get("mobile")
    password = request.POST.get("password")
    password2 = request.POST.get("password2")
    nickname = request.POST.get("nickname")
    print username, "-----------", password

    if password != password2:
        return Response(ApiResult(code=1, msg="两次密码不一致")())
    try:
        exist_user = Profile.objects.filter(nickname=nickname)
        if exist_user:
            return Response(ApiResult(code=1, msg="用户名已存在，请重新选择")())
        new_user = User.objects.create_user(username=username, password=password)
        new_user.profile.nickname = nickname
        new_user.save()
    except django.db.IntegrityError:
        return Response(ApiResult(code=1, msg="手机号已存在,请直接登录")())

    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

    payload = jwt_payload_handler(new_user)
    token = jwt_encode_handler(payload)

    return Response(ApiResult(msg='注册成功', result={'token': token})())


@api_view(["POST"])
@permission_classes((AllowAny,))
def user_login(request):
    username = request.POST.get("mobile")
    password = request.POST.get("password")
    user = auth.authenticate(username=username, password=password)
    if not user:
        return Response(ApiResult(code=1, msg="用户名或密码错误")())
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)
    return Response(ApiResult(msg="登陆成功", result={"token":token})())


@api_view(['GET'])
@permission_classes((AllowAny,))
def gen_sms_code(request):
    mobile = request.GET.get("mobile")
    exist_code = cache.get(mobile)
    sms_code = exist_code if exist_code else create_verify_code()
    cache.set(mobile, sms_code, 60)
    send_result = SMSSender().templateSMS(accountSid=settings.SMS_ACCOUNTSID,
                                          accountToken=settings.SMS_AUTHTOKEN,
                                          appId=settings.SMS_APPID,
                                          toNumbers=mobile,
                                          templateId=settings.SMS_TEMPLATE_ID,
                                          param=sms_code)

    sms_info = json.loads(send_result)
    if sms_info['resp']['respCode'] != "000000":
        return Response(ApiResult(code=1, msg="验证码发送失败，请重试", result={"sms_info": sms_info})())

    else:
        return Response(ApiResult(result={"verify_code": sms_code,
                                          "sms_info": sms_info})())


@api_view(['GET'])
@permission_classes((AllowAny,))
def verify_sms_code(request):
    client_sms_code = request.GET.get("verify_code")
    mobile = request.GET.get("mobile")
    server_sms_code = cache.get(mobile)
    if client_sms_code == server_sms_code:
        return Response(ApiResult(code=0, msg="验证成功")())
    return Response(ApiResult(code=1, msg="验证失败")())


@api_view(['GET'])
@permission_classes((AllowAny,))
def reset_password(request):
    mobile = request.POST.get("mobile")
    password = request.POST.get("password")
    password2 = request.POST.get("password2")
    if password != password2:
        return Response(ApiResult(code=1, msg="两次密码不一致"))
    user = User.objects.get(mobile=mobile)
    if not user:
        return Response(ApiResult(code=1, msg="您的手机尚未注册"))
    user.password = make_password(password)
    user.save()
    return Response(ApiResult(code=0, msg="重置密码成功"))


@api_view(['GET'])
@permission_classes((AllowAny,))
def jipush_sms_verify(request):
    echostr = request.GET.get("echostr")
    return HttpResponse(echostr)