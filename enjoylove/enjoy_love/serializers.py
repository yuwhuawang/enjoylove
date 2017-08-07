#coding:utf-8
from __future__ import unicode_literals
__author__ = 'yuwhuawang'
__created__ = '2017/08/06 14:14'
from rest_framework import serializers
from models import (User, Profile, GlobalSettings,
                    PersonalTag, UserTags, Album,
                    PersonalInterest, UserContact,
                    ContactType, FilterControl)


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


class FilterControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilterControl
        fields = ("id", "name", "param")