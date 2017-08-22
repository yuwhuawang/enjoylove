# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.utils.safestring
from django.contrib import admin

from django.contrib.auth.admin import UserAdmin

from models import (User, Profile, Vip, IdentityVerify,
                    GlobalSettings, PersonalTag, UserTags,
                    Advertisement, UserContact, ContactType,
                    PersonalInterest, UserInterest, Album,
                    FilterControl, FilterOptions)
from django.utils.safestring import mark_safe

# Register your models here.


class ProfileInline(admin.StackedInline):
    model = Profile
    verbose_name = '用户信息'
    list_display = ("nickname", "sex")
    list_filter = ("sex", "vip", "has_child", "has_car")


class UserTagInline(admin.StackedInline):
    model = UserTags
    verbose_name = "用户标签"


class UserInterestInline(admin.StackedInline):
    model = UserInterest
    verbose_name = "用户兴趣爱好"


class UserContactInfoInline(admin.StackedInline):
    model = UserContact
    verbose_name = "用户通讯信息"


class UserAlbumInline(admin.TabularInline):
    model = Album
    verbose_name = "用户相册"
    fields = ("photo_url",)


class UserProfileAdmin(UserAdmin):

    inlines = (ProfileInline, UserTagInline, UserContactInfoInline,
               UserInterestInline, UserAlbumInline)

    def nickname(self, obj):
        return obj.profile.nickname

    def sex(self, obj):
        return obj.profile.get_sex_display()

    def vip(self, obj):
        try:
            return obj.profile.vip.vip_type
        except AttributeError:
            return "-"


    def avatar(self, obj):
        if self.image:
            return mark_safe('<img src="{}" />'.format(obj.profile.avatar))
        else:
            return "默认图片"

    list_display = ("username", "nickname", "sex", "vip")
    list_filter = ("profile__sex", "profile__vip", "profile__has_children", "profile__has_car")

    nickname.short_description = '昵称'
    sex.short_description = '性别'


@admin.register(Vip)
class VipAdmin(admin.ModelAdmin):

    list_display = ("vip_type", "vip_month_price", "vip_month_price_org",
                    "vip_half_year_price", "vip_half_year_price_org",
                    "vip_year_price", "vip_year_price_org",
                    "vip_member_count")
    list_editable = ("vip_month_price", "vip_month_price_org",
                    "vip_half_year_price",  "vip_half_year_price_org",
                    "vip_year_price", "vip_year_price_org",)
    #list_display_links = ("vip_type",)


@admin.register(IdentityVerify)
class IdentityVerifyAdmin(admin.ModelAdmin):
    list_display = ("user", "real_name", "status")


@admin.register(GlobalSettings)
class GlobalSettingAdmin(admin.ModelAdmin):
    list_display = ("key", "value", "desc", "valid")
    list_editable = ("value", "desc")
    list_filter = ("valid", )


@admin.register(PersonalTag)
class PersonTagAdmin(admin.ModelAdmin):
    list_display = ("name", "valid")
    list_filter = ("valid", )


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    exclude = ("create_time", "update_time")
    list_filter = ("valid", "expire_time", "show_place", "show_page", "show_position")


@admin.register(ContactType)
class ContactTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "valid")
    #exclude = ("create_time", "update_time")
    list_filter = ("valid", )


@admin.register(PersonalInterest)
class PersonInterestAdmin(admin.ModelAdmin):
    list_display = ("name", "valid")
    list_filter = ("valid", )


class FilterOptionsInline(admin.StackedInline):
    model = FilterOptions
    verbose_name = "筛选选项"


@admin.register(FilterControl)
class FilterControlAdmin(admin.ModelAdmin):
    inlines = (FilterOptionsInline, )
    list_display = ("name", "param", "valid")
    list_filter = ("valid", )





admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
