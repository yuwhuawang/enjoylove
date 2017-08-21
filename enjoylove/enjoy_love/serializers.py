#coding:utf-8
from __future__ import unicode_literals
__author__ = 'yuwhuawang'
__created__ = '2017/08/06 14:14'
from rest_framework import serializers
from models import (User, Profile, GlobalSettings,
                    PersonalTag, UserTags, Album,
                    PersonalInterest, UserInterest,
                    UserContact,
                    ContactType, FilterControl,
                    FilterOptions, UserMessage,
                    LikeRecord)


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

    tag_id = serializers.IntegerField(source="tag.id")
    tag_name = serializers.CharField(source="tag.name")

    class Meta:
        model = UserTags
        fields = ("tag_id", "tag_name")
        #fields = "__all__"


class PersonalInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalInterest
        fields = ("id", "name", )


class UserInterestSerializer(serializers.ModelSerializer):

    interest_id = serializers.IntegerField(source="interest.id")
    interest_name = serializers.CharField(source="interest.name")
    class Meta:
        model = UserInterest
        fields = ("interest_id", "interest_name")


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
    avatar = serializers.CharField(source="profile.avatar")
    type = serializers.IntegerField(default=1)
    content = serializers.DictField(default={})
    vip = serializers.CharField(source="profile.vip.vip_type")

    class Meta:
        model = User
        fields = ("uid", "account", "identity_verified", "avatar", "nickname", "work_area", "age", "height", "career",
                  "income", "person_intro", "like", "type", "content", "vip")


class PersonDetailSerializer(serializers.ModelSerializer):

    def get_albums(self):
        user = self.context['request'].user
        albums = Album.objects.filter(user=user, deleted=False)
        serializer = AlbumSerializer(instance=albums, many=True)
        return serializer.data

    person_id = serializers.IntegerField(source="id")
    nickname = serializers.CharField(source="profile.nickname")
    person_intro = serializers.CharField(source ="profile.person_intro")
    work_area_name = serializers.CharField(source="profile.work_area_name")
    born_area_name = serializers.CharField(source="profile.born_area_name")
    birth_date = serializers.DateField(source="profile.birth_date")
    identity_verified = serializers.CharField(source="profile.identity_verified")
    age = serializers.IntegerField(source="profile.age")
    height = serializers.IntegerField(source="profile.height")
    career = serializers.CharField(source="profile.get_career_display")
    income = serializers.CharField(source="profile.get_income_display")
    expect_marry_date = serializers.CharField(source="profile.get_expect_marry_date_display")
    nationality = serializers.CharField(source="profile.nationality")
    marriage_status = serializers.CharField(source="profile.get_marriage_status_display")
    birth_index = serializers.CharField(source="profile.birth_index")
    has_children = serializers.CharField(source="profile.get_has_children_display")
    weight = serializers.CharField(source="profile.weight")
    avatar = serializers.CharField(source="profile.avatar")
    vip = serializers.CharField(source="profile.vip.vip_type")
    has_car = serializers.CharField(source="profile.get_has_car_display")
    has_house = serializers.CharField(source="profile.get_has_house_display")
    relationship_desc = serializers.CharField(source="profile.relationship_desc")
    mate_preference = serializers.CharField(source="profile.mate_preference")
    constellation = serializers.CharField(source="profile.get_constellation_display")
    like = serializers.IntegerField(source="profile.like")

    #tags = UserTagSerializer()

    #albums = Album.objects.fitler(deleted=False, )

    class Meta:
        model = User
        fields = ("person_id", "nickname", "person_intro", "identity_verified",
                  "work_area_name", "age", "height", "career",
                  "income", "expect_marry_date", "nationality",
                  "marriage_status", "birth_index", "has_children",
                  "weight", "avatar", "vip", "has_car", "has_house",
                  "relationship_desc", "mate_preference", "constellation",
                  "like", "albums", "born_area_name", "birth_date", "tags")

    def to_representation(self, obj):
        data = super(PersonDetailSerializer, self).to_representation(obj)

        data['tags'] = UserTagSerializer(
            UserTags.objects.filter(user=obj), many=True
        ).data

        data['interests'] = UserInterestSerializer(
            UserInterest.objects.filter(user=obj), many=True
        ).data

        data['albums'] = AlbumSerializer(
            Album.objects.filter(deleted=False, user=obj), many=True).data

        data['messages'] = UserMessageSerializer(
            UserMessage.objects.filter(message_to=obj, deleted=False)[0:3], many=True
        ).data


        return data


class UserMessageSerializer(serializers.ModelSerializer):
    sender_id = serializers.IntegerField(source="message_from.id")
    sender_name = serializers.CharField(source="message_from.profile.nickname")
    sender_avatar = serializers.CharField(source="message_from.profile.avatar")
    receiver_id = serializers.IntegerField(source="message_to.id")
    receiver_name = serializers.CharField(source="message_to.profile.nickname")
    receiver_avatar = serializers.CharField(source="message_to.profile.avatar")

    class Meta:
        model = UserMessage
        fields = ("id", "sender_id", "sender_name", "sender_avatar",
                  "receiver_id", "receiver_name", "receiver_avatar", "content", "create_time",)