#coding:utf-8
from __future__ import unicode_literals
__author__ = 'yuwhuawang'
__created__ = '2017/08/06 14:14'
from rest_framework import serializers
from models import User, Profile, GlobalSettings, PersonalTag, UserTags, Album


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ('id', )


class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    album = AlbumSerializer()

    uid = serializers.IntegerField(source="id")
    account = serializers.CharField(source="username")

    class Meta:
        model = User
        fields = ("uid", "account", "profile", "album")


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