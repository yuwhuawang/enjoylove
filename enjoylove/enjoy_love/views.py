# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.core.cache
import django.db
import django.http
import rest_framework.permissions
from rest_framework.response import Response
import rest_framework_jwt.views
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import render
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from enjoy_love.utils import create_verify_code
import enjoy_love.utils
from enjoy_love.api_result import ApiResult
from django.core.cache import cache

# Create your views here.
import enjoy_love.api_result
import enjoy_love.models
from enjoy_love.models import User
from django.http import HttpResponse


def user_demo(request):
    desc = User.objects.all()[0]
    return HttpResponse(desc)


@api_view(['POST'])
@permission_classes((AllowAny,))
def user_register(request):
    username = request.POST.get("mobile")
    password = request.POST.get("password")
    nickname = request.POST.get("nickname")
    print username, "--------", password
    new_user = User()
    new_user.username = username
    new_user.password = password
    new_user.nickname = nickname
    try:
        new_user.save()
    except django.db.IntegrityError:
        return Response(ApiResult(code=1, msg="手机号已存在,请直接登录")())

    from rest_framework_jwt.settings import api_settings

    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

    payload = jwt_payload_handler(new_user)
    token = jwt_encode_handler(payload)

    return Response(ApiResult(msg='注册成功', result={'token': token})())


@api_view(['GET'])
@permission_classes((AllowAny,))
def gen_sms_code(request):
    mobile = request.GET.get("mobile")
    exist_code = cache.get(mobile)
    sms_code = exist_code if exist_code else create_verify_code()
    cache.set(mobile, sms_code, 60)
    #todo send_sms_code
    return Response(ApiResult(result={"sms_code": sms_code})())


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
def jipush_sms_verify(request):
    echostr = request.GET.get("echostr")
    return HttpResponse(echostr)