# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.core.cache
import django.db
import django.db.transaction
import django.http
import logging
import simplejson as json
from django.contrib import auth
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from enjoy_love.util import create_verify_code
from enjoy_love.api_result import ApiResult
from django.core.cache import cache

# Create your views here.
from enjoy_love.models import User, Profile, IdentityVerify, GlobalSettings, PersonalTag, UserTags
from django.contrib.auth.hashers import make_password
from rest_framework_jwt.settings import api_settings

from utils.sms import RestAPI as SMSSender
from django.conf import settings

from serializers import UserSerializer, GlobalSerializer, PersonalTagSerializer, UserTagSerializer


def test(request):
    sms_sender = SMSSender()
    sms_sender.templateSMS(accountSid=settings.SMS_ACCOUNTSID,
                           accountToken=settings.SMS_AUTHTOKEN,
                           appId=settings.SMS_APPID,
                           toNumbers="17600369907",
                           templateId=settings.SMS_TEMPLATE_ID,
                           param="111111")


@api_view(['GET'])
@permission_classes((AllowAny,))
def init(request):
    global_settings = GlobalSettings.objects.filter(valid=True)
    personal_tags = PersonalTag.objects.filter(valid=True)

    global_setting_data = GlobalSerializer(global_settings, many=True)
    personal_tags_data = PersonalTagSerializer(personal_tags, many=True)

    return ApiResult(result={
        "global_settings": global_setting_data.data,
        "personal_tags": personal_tags_data.data
    })


@api_view(['POST'])
@permission_classes((AllowAny,))
def user_register(request):
    username = request.POST.get("mobile")
    password = request.POST.get("password")
    password2 = request.POST.get("password2")
    nickname = request.POST.get("nickname")
    print username, "-----------", password

    if password != password2:
        return ApiResult(code=1, msg="两次密码不一致")
    try:
        exist_user = Profile.objects.filter(nickname=nickname)
        if exist_user:
            return ApiResult(code=1, msg="用户名已存在，请重新选择")
        new_user = User.objects.create_user(username=username, password=password)
        new_user.profile.nickname = nickname
        new_user.save()
    except django.db.IntegrityError:
        return ApiResult(code=1, msg="手机号已存在,请直接登录")

    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

    payload = jwt_payload_handler(new_user)
    token = jwt_encode_handler(payload)

    return ApiResult(msg='注册成功', result={'token': token})


@api_view(["POST"])
@permission_classes((AllowAny,))
def user_login(request):
    username = request.POST.get("mobile")
    password = request.POST.get("password")
    user = auth.authenticate(username=username, password=password)
    if not user:
        return ApiResult(code=1, msg="用户名或密码错误")
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)
    userserializer = UserSerializer(user)

    return ApiResult(msg="登陆成功", result={"token":token,
                                           "user_info": userserializer.data})


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
        return ApiResult(code=1, msg="验证码发送失败，请重试", result={"sms_info": sms_info})

    else:
        return ApiResult(result={"verify_code": sms_code,
                                          "sms_info": sms_info})


@api_view(['GET'])
@permission_classes((AllowAny,))
def verify_sms_code(request):
    client_sms_code = request.GET.get("verify_code")
    mobile = request.GET.get("mobile")
    server_sms_code = cache.get(mobile)
    if client_sms_code == server_sms_code:
        return ApiResult(code=0, msg="验证成功")
    return ApiResult(code=1, msg="验证失败")


@api_view(['GET'])
@permission_classes((AllowAny,))
def reset_password(request):
    mobile = request.POST.get("mobile")
    password = request.POST.get("password")
    password2 = request.POST.get("password2")
    if password != password2:
        return ApiResult(code=1, msg="两次密码不一致")
    user = User.objects.get(mobile=mobile)
    if not user:
        return ApiResult(code=1, msg="您的手机尚未注册")
    user.password = make_password(password)
    user.save()
    return ApiResult(code=0, msg="重置密码成功")


@api_view(['POST'])
def upload_avatar(request):
    uid = request.POST.get("uid")
    avatar_url = request.POST.get("avatar")

    user = User.objects.get(pk=uid)
    user.profile.avatar = avatar_url
    user.profile.save()
    return ApiResult(msg="上传成功")


@api_view(['POST'])
def set_gender(request):
    uid = request.POST.get("uid")
    gender = request.POST.get("gender")
    if gender not in ["0", "1", "2"]:
        return ApiResult(code=1, msg="性别选择错误")
    user = User.objects.get(pk=uid)
    user.profile.sex = gender
    user.profile.save()
    return ApiResult(msg="设置成功")


@api_view(['POST'])
def verify_identity(request):
    uid = request.POST.get("uid")
    id_number = request.POST.get("id_number")
    real_name = request.POST.get("real_name")
    img_front = request.POST.get("img_front")
    img_back = request.POST.get("img_back")
    user = User.objects.get(pk=uid)
    verify_records = IdentityVerify.objects.filter(user__id=uid, status=0).count()
    if verify_records:
        return ApiResult(code=1, msg="已申请")
    new_verify = IdentityVerify(user=user, id_number=id_number, real_name=real_name, img_front=img_front, img_back=img_back)
    new_verify.save()
    return ApiResult(msg="申请成功")


@api_view(['POST'])
def set_basic_info(request):
    uid = request.POST.get("uid")
    nickname = request.POST.get("nickname")
    work_area_name = request.POST.get("work_area_name")
    work_area_code = request.POST.get("work_area_code")
    born_area_name = request.POST.get("born_area_name")
    born_area_code = request.POST.get("born_area_code")
    height = request.POST.get("height")
    education = request.POST.get("education")
    career = request.POST.get("career")
    income = request.POST.get("income")
    expect_marry_date = request.POST.get("expect_marry_date")
    nationality = request.POST.get("nationality")
    marriage_status = request.POST.get("marriage_status")
    birth_index = request.POST.get("birth_index")
    has_children = request.POST.get("has_children")
    weight = request.POST.get("weight")
    relationship_desc = request.POST.get("relationship_desc")
    mate_preference = request.POST.get("mate_preference")
    has_car = request.POST.get("has_car")
    has_house = request.POST.get("has_house")

    user = User.objects.get(pk=uid)

    if nickname:
        profile = Profile.objects.filter(nickname=nickname)
        if profile.count():
            return ApiResult(code=1, msg="昵称已存在")

    user.profile.nickname = nickname if nickname else user.profile.nickname
    user.profile.work_area_name = work_area_name if work_area_name else user.profile.work_area_name
    user.profile.work_area_code = work_area_code if work_area_code else user.profile.work_area_code
    user.profile.born_area_name = born_area_name if born_area_name else user.profile.born_area_name
    user.profile.born_area_code = born_area_code if born_area_code else user.profile.born_area_code
    user.profile.height = height if height else user.profile.height
    user.profile.education = education if education else user.profile.education
    user.profile.career = career if career else user.profile.career
    user.profile.income = income if income else user.profile.income
    user.profile.expect_marry_date = expect_marry_date if expect_marry_date else user.profile.expect_marry_date
    user.profile.nationality = nationality if nationality else user.profile.nationality
    user.profile.marriage_status = marriage_status if marriage_status else user.profile.marriage_status
    user.profile.birth_index = birth_index if birth_index else user.profile.birth_index
    user.profile.has_children = has_children if has_children else user.profile.has_children
    user.profile.weight = weight if weight else user.profile.weight
    user.profile.relationship_desc = relationship_desc if relationship_desc else user.profile.relationship_desc
    user.profile.mate_preference = mate_preference if mate_preference else user.profile.mate_preference
    user.profile.has_car = has_car if has_car else user.profile.has_car
    user.profile.has_house = has_house if has_house else user.profile.has_house
    user.profile.save()

    return ApiResult("修改成功")


@api_view(['GET'])
def get_user_tags(request):
    uid = request.GET.get("uid")
    user_tags = UserTags.objects.filter(user_id=uid)
    user_tags_data = UserTagSerializer(user_tags, many=True).data
    return ApiResult(result=user_tags_data)


@api_view(['POST'])
def set_user_tags(request):
    uid = request.POST.get("uid")
    tag_ids = request.POST.get("tag_ids")

    UserTags.objects.filter(user_id=uid).delete()

    if tag_ids:
        raise Exception
        tag_ids_list = tag_ids.split(',')
        if len(tag_ids_list) > 8:
            return ApiResult(msg="最多可以选择八个")

        for tag_id in tag_ids_list:
            try:
                UserTags(user_id=uid, tag_id=tag_id).save()
            except django.db.IntegrityError as e:
                logging.error(str(e))
                #return ApiResult(error=str(e))

    return ApiResult()



