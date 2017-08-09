#coding:utf-8
from __future__ import unicode_literals
__author__ = 'yuwhuawang'
__created__ = '2017/08/06 14:14'
from rest_framework import serializers
from models import (User, Profile, GlobalSettings,
                    PersonalTag, UserTags, Album,
                    PersonalInterest, UserContact,
                    ContactType, FilterControl,
                    FilterOptions)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ('id', "user")


class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ("id", "photo_url")
        #fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    albums = AlbumSerializer(many=True, read_only=True)

    uid = serializers.IntegerField(source="id")
    account = serializers.CharField(source="username")

    class Meta:
        model = User
        fields = ("uid", "account", "profile", "albums")


class GlobalSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalSettings
        fields = "__all__"


class PersonalTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalTag
        fields = ("id", "name")


class UserTagSerializer(serializers.ModelSerializer):
    tag = PersonalTagSerializer()

    class Meta:
        model = UserTags
        fields = ("tag", )
        #fields = "__all__"


class PersonalInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalInterest
        fields = ("id", "name", )


class PersonalContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactType
        fields = ("id", "name", )


class UserContactSerializer(serializers.ModelSerializer):
    #contacts = PersonalInterestSerializer(many=True, read_only=True)
    #contacts = serializers.StringRelatedField(many=True, read_only=True)

    name = serializers.CharField(source="type.name")
    uid = serializers.IntegerField(source="user.id")

    class Meta:
        model = UserContact
        fields = ("id", "uid", "name", "content")


class FilterOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilterOptions
        fields = ("option_name", "option_value")


class FilterControlSerializer(serializers.ModelSerializer):
    filter_options = FilterOptionSerializer(many=True, read_only=True)

    class Meta:
        model = FilterControl
        fields = ("id", "name", "param", "filter_options")


class PersonListSerializer(serializers.ModelSerializer):
    #profile = ProfileSerializer()
    #albums = AlbumSerializer(many=True, read_only=True)

    uid = serializers.IntegerField(source="id")
    account = serializers.CharField(source="username")
    identity_verified = serializers.IntegerField(source="profile.identity_verified")
    nickname = serializers.CharField(source="profile.nickname")
    work_area = serializers.CharField(source="profile.work_area_name")
    age = serializers.IntegerField(source="profile.age")
    height = serializers.IntegerField(source="profile.height")
    career = serializers.CharField(source="profile.career")
    income = serializers.CharField(source="profile.income")
    person_intro = serializers.CharField(source="profile.person_intro")
    like = serializers.IntegerField(source="profile.like")
    type = serializers.IntegerField(default=1)
    content = serializers.DictField(default={})

    class Meta:
        model = User
        fields = ("uid", "account", "identity_verified", "nickname", "work_area", "age", "height", "career", "income", "person_intro", "like", "type", "content")

