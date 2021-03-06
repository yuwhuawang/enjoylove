# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db
import django.db.models
import django.db.transaction
import django.http
import logging

import rest_framework.views
import simplejson as json
from django.contrib import auth
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from enjoy_love.util import create_verify_code
from enjoy_love.api_result import ApiResult, BusinessError
#from django.core.cache import cache
from django.db import transaction
from django.core import cache
from django.core.paginator import Paginator, EmptyPage
# Create your views here.
from models import (User, Profile, IdentityVerify,
                    GlobalSettings, PersonalTag,
                    UserTags, Album, PersonalInterest,
                    UserInterest, UserContact, FilterControl,
                    Advertisement, LikeRecord, UserMessage,
                    ContactExchange, FeedBack, ContactType)
from django.contrib.auth.hashers import make_password
from rest_framework_jwt.settings import api_settings


from utils.sms import RestAPI as SMSSender
from django.conf import settings

from serializers import (UserSerializer, GlobalSerializer,
                         PersonalTagSerializer, UserTagSerializer,
                         AlbumSerializer, PersonalInterestSerializer,
                         UserContactSerializer, FilterControlSerializer,
                         PersonListSerializer, PersonDetailSerializer,
                         UserInterestSerializer, UserMessageSerializer)

import datetime
from collections import OrderedDict, defaultdict

from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView



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
    personal_interests = PersonalInterest.objects.filter(valid=True)
    filters = FilterControl.objects.filter(valid=True)

    global_setting_data = GlobalSerializer(global_settings, many=True)
    personal_tags_data = PersonalTagSerializer(personal_tags, many=True)
    personal_interests_data = PersonalInterestSerializer(personal_interests, many=True)
    filters_data = FilterControlSerializer(filters, many=True)

    return ApiResult(result={
        "global_settings": global_setting_data.data,
        "personal_tags": personal_tags_data.data,
        "personal_interests": personal_interests_data.data,
        "filters": filters_data.data
    })


@api_view(['GET'])
@permission_classes((AllowAny, ))
def user_init(request):
    uid = request.GET.get("uid")
    user_info = dict()
    if uid:
        user = User.objects.get(pk=uid)
        user_info = UserSerializer(user).data

    global_settings = GlobalSettings.objects.filter(valid=True)
    personal_tags = PersonalTag.objects.filter(valid=True)
    personal_interests = PersonalInterest.objects.filter(valid=True)
    filters = FilterControl.objects.filter(valid=True)

    global_setting_data = GlobalSerializer(global_settings, many=True).data
    personal_tags_data = PersonalTagSerializer(personal_tags, many=True).data
    psesonal_interests_data = PersonalInterestSerializer(personal_interests, many=True)
    filters_data = FilterControlSerializer(filters, many=True)

    return ApiResult(result = {"user_info": user_info,
                      "global_info": global_setting_data,
                      "personal_tags": personal_tags_data,
                      "personal_interests": psesonal_interests_data.data,
                      "filters": filters_data.data
                      })


@api_view(['POST'])
@permission_classes((AllowAny,))
@transaction.atomic
def user_register(request):
    username = request.POST.get("mobile")
    password = request.POST.get("password")
    password2 = request.POST.get("password2")
    nickname = request.POST.get("nickname", "")
    device_id = request.META.get("device_id", "")
    platform = request.META.get("platform", "")
    version_code = request.META.get("version_code", "")
    print username, "-----------", password

    if password != password2:
        return ApiResult(code=1, msg="两次密码不一致")
    try:
        exist_user = Profile.objects.filter(nickname=nickname)
        if exist_user:
            return ApiResult(code=1, msg="用户名已存在，请重新选择")
        new_user = User.objects.create_user(username=username, password=password)
        new_user.profile.nickname = nickname
        new_user.profile.device_id = device_id
        new_user.profile.platform = platform
        new_user.profile.version_code = version_code
        new_user.profile.save()

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
    device_id = request.META.get("device_id", "")
    platform = request.META.get("platform", "")
    version_code = request.META.get("version_code", "")
    user = auth.authenticate(username=username, password=password)
    if not user:
        return ApiResult(code=1, msg="用户名或密码错误")
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)
    userserializer = UserSerializer(user)
    user.profile.device_id = device_id
    user.profile.platform = platform
    user.profile.version_code = version_code

    return ApiResult(msg="登陆成功", result={"token":token,
                                           "user_info": userserializer.data})


@api_view(['GET'])
@permission_classes((AllowAny,))
def gen_sms_code(request):
    mobile = request.GET.get("mobile")
    exist_code = cache.cache.get(mobile)
    sms_code = exist_code if exist_code else create_verify_code()
    cache.cache.set(mobile, sms_code, 60)
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
    server_sms_code = cache.cache.get(mobile)
    if client_sms_code == server_sms_code:
        return ApiResult(code=0, msg="验证成功")
    return ApiResult(code=1, msg="验证失败")


@api_view(['POST'])
@permission_classes((AllowAny,))
def forgot_password(request):
    mobile = request.POST.get("mobile")
    client_sms_code = request.GET.get("verify_code")
    password = request.POST.get("password")
    server_sms_code = cache.cache.get(mobile)
    if client_sms_code != server_sms_code:
        return BusinessError("验证失败")
    user = User.objects.get(mobile=mobile)
    if not user:
        return ApiResult(code=1, msg="您的手机尚未注册")
    user.password = make_password(password)
    user.save()
    return ApiResult(code=0, msg="重置密码成功")


@api_view(['POST'])
def reset_password(request):
    mobile = request.POST.get("mobile")
    old_password = request.POST.get("old_pwd")
    user = auth.authenticate(username=mobile, password=old_password)
    if not user:
        return BusinessError("用户名或密码不正确")

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
    birth_date = request.POST.get("birth_date")
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
    person_intro = request.POST.get("person_intro")
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
    user.profile.person_intro = person_intro if person_intro else user.profile.person_intro
    user.profile.birth_date = birth_date if birth_date else user.profile.birth_date

    user.profile.save()

    return ApiResult("修改成功")


@api_view(['GET'])
def get_user_tags(request):
    uid = request.GET.get("uid")
    user_tags = UserTags.objects.filter(user_id=uid)

    user_tags_data = UserTagSerializer(user_tags, many=True).data

    #user_tags_data_list = [i['tag'] for i in user_tags_data]
    return ApiResult(result=user_tags_data)


@api_view(['POST'])
@transaction.atomic
def set_user_tags(request):
    uid = request.POST.get("uid")
    tag_ids = request.POST.get("tag_ids")

    UserTags.objects.filter(user_id=uid).delete()

    if tag_ids:
        tag_ids_list = tag_ids.split(',')
        if len(tag_ids_list) > 8:
            return ApiResult(code=1, msg="最多可以选择八个")

        for tag_id in tag_ids_list:
            try:
                UserTags(user_id=uid, tag_id=tag_id).save()
            except django.db.IntegrityError as e:
                logging.error(str(e))

    return ApiResult()


@api_view((['GET']))
def get_user_interests(request):
    uid = request.GET.get("uid")
    user_interests = UserInterest.objects.filter(user_id=uid)
    user_interests_data = UserInterestSerializer(user_interests, many=True).data
    return ApiResult(result=user_interests_data)


@api_view(['POST'])
@transaction.atomic
def set_user_interests(request):
    uid = request.POST.get("uid")
    interest_ids = request.POST.get("interest_ids")

    UserInterest.objects.filter(user_id=uid).delete()

    if interest_ids:
        interest_ids_list = interest_ids.split(',')
        if len(interest_ids_list) > 8:
            return ApiResult(code=1, msg="最多可以选择八个")

        for interest_id in interest_ids_list:
            try:
                UserTags(user_id=uid, interest_id=interest_id).save()
            except django.db.IntegrityError as e:
                logging.error(str(e))


@api_view(['GET'])
def user_album(request):
    uid = request.GET.get("uid")
    album = Album.objects.filter(deleted=False, user__id=uid)
    return ApiResult(result=AlbumSerializer(album, many=True).data)


@api_view(["POST"])
def set_album(request):
    uid = request.POST.get("uid")
    photo_url = request.POST.get("photo_url")
    exist_albums = Album.objects.filter(deleted=False, user__id=uid)
    if exist_albums.count() >= 8:
        return ApiResult(code=1, msg="您最多只能上传8张照片")
    album = Album(user__id=uid, photo_url=photo_url)
    album.save()
    return ApiResult()


@api_view(["POST"])
def delete_album(request):
    uid = request.POST.get("uid")
    photo_ids = request.POST.get("photo_ids")
    if not photo_ids:
        return BusinessError("请传入photo_ids")
    photo_ids = photo_ids.split(",")
    result = list()

    for photo_id in photo_ids:
        try:
            album = Album.objects.get(pk=photo_id)
        except:
            result.append({"photo_id": photo_id, "result": "照片不存在"})
            continue
        if album.deleted:
            result.append({"photo_id": photo_id, "result": "照片已被删除"})

            continue

        if album.user.id != uid:
            result.append({"photo_id": photo_id, "result": "无权删除"})
            continue

        album.deleted = True
        album.save()
        result.append({"photo_id": photo_id, "result": "删除成功"})
    return ApiResult(result={"status": result})


@api_view(["GET"])
def user_contact(request):
    uid = request.GET.get("uid")
    user_contacts = UserContact.objects.filter(user__id=uid, deleted=False)
    user_contacts = UserContactSerializer(user_contacts, many=True)
    return ApiResult({"contacts": user_contacts.data})


@api_view(["POST"])
def set_contact(request):
    uid = request.POST.get("uid")
    contact_name = request.POST.get("type")
    contact_content = request.POST.get("content")

    try:
        contact = UserContact.objects.get(user__id=uid, type__name=contact_name)
        contact.content = contact_content
        contact.save()
    except UserContact.DoesNotExist:
        contact_type = ContactType.object.get(name=contact_name)
        contact = UserContact()
        contact.user_id = uid
        contact.type = contact_type
        contact.content = contact_content
        contact.save()

    return ApiResult("设置成功")


class SetContactView(APIView):

    def post(self, request):
        uid = request.POST.get("uid")
        qq = request.POST.get("qq")
        weixin = request.POST.get("weixin")
        mobile = request.POST.get("mobile")

        if qq:
             try:
                contact = UserContact.objects.get(user__id=uid, type__name="QQ")
                contact.content = qq
                contact.save()
             except UserContact.DoesNotExist:
                contact_type = ContactType.objects.get(name="QQ")
                contact = UserContact()
                contact.user_id = uid
                contact.type = contact_type
                contact.content = qq
                contact.save()
        if weixin:
            try:
                contact = UserContact.objects.get(user__id=uid, type__name="微信")
                contact.content = weixin
                contact.save()
            except UserContact.DoesNotExist:
                contact_type = ContactType.objects.get(name="微信")
                contact = UserContact()
                contact.user_id = uid
                contact.type = contact_type
                contact.content = weixin
                contact.save()

        if mobile:
            try:
                contact = UserContact.objects.get(user__id=uid, type__name="mobile")
                contact.content = mobile
                contact.save()
            except UserContact.DoesNotExist:
                contact_type = ContactType.objects.get(name="mobile")
                contact = UserContact()
                contact.user_id = uid
                contact.type = contact_type
                contact.content = mobile
                contact.save()

        return ApiResult()


@api_view(["POST"])
def delete_contact(request):
    uid = request.POST.get("uid")
    contact_name = request.POST.get("type")
    #contact_content = request.POST.get("content")

    contact = UserContact.objects.get(user__id=uid, type__name=contact_name)
    contact.deleted = True
    contact.save()
    return ApiResult("设置成功")


@api_view(["GET"])
@permission_classes((AllowAny, ))
def person_list(request):
    uid = request.GET.get("uid")

    offset = request.GET.get("offset", 0)
    limit = request.GET.get("limit", 10)

    is_student = request.GET.get("is_student")
    sex = request.GET.get("sex")
    min_age = request.GET.get("min_age")
    max_age = request.GET.get("max_age")
    work_area_code = request.GET.get("work_area_code")
    born_area_code = request.GET.get("born_area_code")
    min_height = request.GET.get("min_height")
    max_height = request.GET.get("max_height")
    #education = request.GET.get("education")
    min_education = request.GET.get("min_education")
    max_education = request.GET.get("max_education")
    career = request.GET.get("career")
    income = request.GET.get("income")
    expect_marry_date = request.GET.get("expect_marry_date")
    nationality = request.GET.get("nationality")
    marriage_status = request.GET.get("marriage_status")
    birth_index = request.GET.get("birth_index")
    min_weight = request.GET.get("min_weight")
    max_weight = request.GET.get("max_weight")
    has_car = request.GET.get("has_car")
    has_children = request.GET.get("has_children")
    has_house = request.GET.get("has_house")


    query_params = dict()
    #query_params['id'] = uid

    if sex:
        query_params['profile__sex'] = sex
    if min_age:
        query_params['profile__age__gte'] = min_age
    if max_age:
        query_params['profile__age__lte'] = max_age
    if work_area_code:
        query_params['profile__work_area_code'] = work_area_code
    if born_area_code:
        query_params['profile__born_area_code'] = born_area_code

    if min_height:
        query_params['profile__min_height__gte'] = min_height
    if max_height:
        query_params['profile__max_height__lte'] = max_height
    #if education:
    #    query_params['profile__education'] = education
    if min_education:
        query_params['profile__education__gte'] = min_education
    if max_education:
        query_params['profile__education__lte'] = max_education
    if career:
        query_params['profile__career'] = career
    if income:
        query_params['profile__income'] = income
    if expect_marry_date:
        query_params['profile__expect_marry_date'] = expect_marry_date
    if nationality:
        query_params['profile__nationality'] = nationality
    if marriage_status:
        query_params['profile__marriage_status'] = marriage_status
    if birth_index:
        query_params['profile__birth_index'] = birth_index
    if min_weight:
        query_params['profile__min_weight__gte'] = min_weight
    if max_weight:
        query_params['profile__max_weight__lte'] = max_weight
    if has_car:
        query_params['profile__has_car'] = has_car
    if has_children:
        query_params['profile__has_children'] = has_children
    if has_house:
        query_params['profile__has_house'] = has_house

    if is_student is not None:
        if is_student == 0:
            query_params["profile__career"] = 0
        if is_student == 1:
            query_params["profile_career__in"] = [0, 2, 3, 4, 5, 6]

    total_size = User.objects.filter(**query_params).count()

    page = int(offset) + 1
    limit = int(limit)

    #tops = User.objects.filter(profile__on_top=True, **query_params)
    user_list = User.objects.filter(**query_params).order_by("-profile__on_top", "?")

    paginator = Paginator(user_list, limit)
    try:
        person_list = PersonListSerializer(paginator.page(page), many=True).data
        for person in person_list:
            is_like = False
            like_record = cache.cache.get("{}_like_{}".format(uid, person['uid']))
            if like_record is None:
                try:
                    like_record = LikeRecord.objects.get(like_from_id=uid,
                                                         like_to_id=person['uid'])
                    is_like = True
                    cache.cache.set("{}_like_{}".format(uid, person['uid']), True, 60*10)
                except LikeRecord.DoesNotExist:
                        cache.cache.set("{}_like_{}".format(uid, person['uid']), False, 60*10)
                person['is_like'] = is_like
            else:
                person['is_like'] = like_record

    except EmptyPage:
        return BusinessError("没有更多数据")

    advertisements = Advertisement.objects.filter(valid=True, expire_time__gt=datetime.datetime.now(),  show_place__in=[0, 1], show_page=page)

    for ad in advertisements:
        ad_result = OrderedDict()
        ad_result["uid"] = 0
        ad_result["account"] = ""
        ad_result["identity_verified"] = ""
        ad_result["nickname"] = ""
        ad_result["work_area"] = ""
        ad_result["age"] = ""
        ad_result["height"] = 0
        ad_result["career"] = 0
        ad_result["income"] = 0
        ad_result["person_intro"] = 0
        ad_result["like"] = 0
        ad_result["type"] = 2
        ad_result["content"] = {
            "name": ad.name,
            "img": ad.img,
            "desc": ad.desc,
            "url": ad.url
        }
        ad_position = ad.show_position if ad.show_position <= limit else limit
        person_list.insert(ad_position, ad_result)

    return ApiResult(result={"total": total_size,
                             "person_list": person_list})


@api_view(["GET"])
@permission_classes((AllowAny,))
def person_detail(request, person_id):
    liked = False
    can_leave_message = False
    contact_result = []
    qq_result = {"type_id": 1, "type_name": "QQ", "status": 0, "content": None}
    wechat_result = {"type_id": 2, "type_name": "微信", "status": 0, "content": None}

    try:
        person = User.objects.get(pk=person_id)
        person_detail = PersonDetailSerializer(person).data
    except Exception as e:
        logging.error(str(e))
        return BusinessError("无此人物", error=str(e))
    uid = request.GET.get("uid")
    if uid:
        like_record = cache.cache.get("{}_like_{}".format(uid, person_id))
        if like_record is None:
            like_record = LikeRecord.objects.filter(like_from__id=uid, like_to__id=person_id)
        if like_record:
            liked = True
            cache.cache.set("{}_like_{}".format(uid, person_id), True, 60*10)
        else:
            cache.cache.set("{}_like_{}".format(uid, person_id), False, 60*10)
        can_leave_message = True

    qq_exchange = ContactExchange.objects.filter(Q(exchange_type__name="QQ"),
                                                 Q(exchange_sender_id=uid) & Q(exchange_receiver_id=person_id) |
                                                 Q(exchange_sender_id=person_id) & Q(exchange_receiver_id=uid)
                                                 ).order_by("-create_time")

    wechat_exchange = ContactExchange.objects.filter(Q(exchange_type__name="微信"),
                                                 Q(exchange_sender_id=uid) & Q(exchange_receiver_id=person_id) |
                                                 Q(exchange_sender_id=person_id) & Q(exchange_receiver_id=uid)
                                                 ).order_by("-create_time")

    if qq_exchange:
        if qq_exchange[0].exchange_status == 1:
            qq_contact = UserContact.objects.filter(user_id=person_id, type__name="QQ", deleted=False)
            qq_result['status'] = 1
            if qq_contact:
                qq_result['content'] = qq_contact[0].content

        elif qq_exchange[0].exchange_status == 2:
            qq_result['status'] = 2

    if wechat_exchange:
        if wechat_exchange[0].exchange_status == 1:
            wechat_contact = UserContact.objects.filter(user_id=person_id, type__name="微信", deleted=False)
            wechat_result['status'] = 1
            if wechat_contact:
                wechat_result['content'] = wechat_contact[0].content
        elif wechat_exchange[0].exchange_status == 2:
            wechat_result['status'] = 2

    person_detail['is_like'] = liked
    person_detail['can_leave_message'] = can_leave_message
    person_detail['contact_result'] = [qq_result, wechat_result]

    return ApiResult(result=person_detail)


@api_view(["POST"])
def set_like(request, person_id):
    uid = request.POST.get("uid")
    like_record = LikeRecord.objects.filter(like_from__id=uid,
                                            like_to__id=person_id)
    if like_record:
        return BusinessError("已经喜欢过")
    new_like = LikeRecord()
    new_like.like_from_id = uid
    new_like.like_to_id = person_id
    new_like.save()
    cache.cache.set("{}_like_{}".format(uid, person_id), True, 60*10)
    return ApiResult()


@api_view(["POST"])
@transaction.atomic
def set_unlike(request, person_id):
    uid = request.POST.get("uid")
    like_record = LikeRecord.objects.filter(like_from__id=uid, like_to__id=person_id)
    if not like_record:
        return BusinessError("未喜欢过")
    like_record.delete()
    user = User.objects.get(pk=person_id)
    user.profile.like -= 1
    user.profile.save()
    cache.cache.set("{}_like_{}".format(uid, person_id), False, 60*10)
    return ApiResult()


@api_view(['POST'])
def leave_message(request, person_id):

    uid = request.POST.get("uid")
    message = request.POST.get("message")
    key = "{}_{}".format(uid, person_id)

    if cache.cache.get(key):
        return BusinessError("您的发言次数过快")
    message_record = UserMessage()
    message_record.message_from_id = uid
    message_record.message_to_id = person_id
    message_record.content = message
    message_record.save()
    cache.cache.set(key, 1, 5)

    return ApiResult("留言成功")


@api_view(['GET'])
def messages_sent(request):
    uid = request.GET.get("uid")
    offset = request.GET.get("offset", 0)
    limit = request.GET.get("limit", 10)
    out_message_records = UserMessage.objects.filter(message_from_id=uid, deleted=False)
    page = int(offset) + 1
    limit = int(limit)
    paginator = Paginator(out_message_records, limit)
    try:
        out_message_records = UserMessageSerializer(paginator.page(page), many=True).data
    except EmptyPage:
        return BusinessError("没有更多数据")

    return ApiResult(result=out_message_records)


@api_view(['GET'])
def messages_received(request):
    uid = request.GET.get("uid")
    offset = request.GET.get("offset", 0)
    limit = request.GET.get("limit", 10)
    page = int(offset) + 1
    limit = int(limit)
    received_message_records = UserMessage.objects.filter(message_to_id=uid, deleted=False)
    paginator = Paginator(received_message_records, limit)
    try:
        received_message_records = UserMessageSerializer(paginator.page(page), many=True).data
    except EmptyPage:
        return BusinessError("没有更多数据")
    return ApiResult(result=received_message_records)


@api_view(["POST"])
def delete_message(request):
    uid = request.GET.get("uid")
    message_id = request.POST.get("message_id")

    try:
        user_message = UserMessage.objects.get(pk=message_id, deleted=False)
    except UserMessage.DoesNotExist as e:
        logging.error(str(e))
        return BusinessError(msg="未查找到留言", error=str(e))
    if user_message.message_to_id != uid:
        return BusinessError("无权删除")
    user_message.deleted = True
    user_message.save()
    return ApiResult()


@api_view(['POST'])
@transaction.atomic
def ask_contact(request, person_id):
    uid = request.POST.get("uid")
    contact_type = request.POST.get("contact_type")

    exist_request = ContactExchange.objects.select_for_update().filter(exchange_sender_id=uid,
                                                   exchange_receiver_id=person_id,
                                                   exchange_type_id=contact_type,
                                                   exchange_status=0)
    if exist_request:
        return BusinessError("您已经申请过")
    contact_request = ContactExchange()
    contact_request.exchange_sender_id = uid
    contact_request.exchange_receiver_id = person_id
    contact_request.exchange_type_id = contact_type
    contact_request.save()
    return ApiResult()


@api_view(['POST'])
def accept_contact(request, person_id):
    uid = request.POST.get("uid")
    contact_type = request.POST.get("contact_type")
    exchange_contacts = ContactExchange.objects.filter(exchange_sender_id=person_id, exchange_receiver_id=uid, exchange_type_id=contact_type, exchange_status=0)
    if not exchange_contacts:
        return BusinessError("无此申请")

    user_contact = UserContact.objects.filter(user_id=uid, type_id=contact_type, deleted=False)
    if not user_contact:
        return BusinessError("请先设置联系方式")

    exchange_contacts.update(exchange_status=1)
    return ApiResult()


@api_view(['POST'])
def deny_contact(request, person_id):
    uid = request.POST.get("uid")
    contact_type = request.POST.get("contact_type")
    exchange_contacts = ContactExchange.objects.filter(exchange_sender_id=person_id, exchange_receiver_id=uid, exchange_type_id=contact_type, exchange_status=0)

    #user_contact = UserContact.objects.filter(user_id=uid, type_id=contact_type, deleted=False)
    #if not user_contact:
        #return BusinessError("请先设置联系方式")

    exchange_contacts.update(exchange_status=2)
    return ApiResult()


class FeedBackView(APIView):
    def post(self, request):
        uid = request.POST.get("uid")
        msg = request.POST.get("msg")
        photo_1 = request.POST.get("photo_1")
        photo_2 = request.POST.get("photo_2")

        FeedBack.objects.create(
            user_id=uid,
            msg=msg,
            photo_1=photo_1,
            photo_2=photo_2
        )
        return ApiResult()

from qiniu import Auth


class GetQiNiuTokenView(APIView):

    def get(self, request):
        bucket = request.GET.get("bucket", settings.QINIU['default_bucket'])
        key = request.GET.get("key")
        expires = request.GET.get("expires", 3600)
        q = Auth(settings.QINIU['access_key'], settings.QINIU['secret_key'])
        token = q.upload_token(bucket, key=key, expires=int(expires))
        return ApiResult(result ={"token": token})









