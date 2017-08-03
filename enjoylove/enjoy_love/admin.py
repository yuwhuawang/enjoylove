# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from models import Profile, Vip

# Register your models here.


class ProfileInline(admin.StackedInline):
    model = Profile
    verbose_name = '用户信息'
    list_display = ("nickname", "sex")


class UserProfileAdmin(UserAdmin):
    inlines = (ProfileInline, )

    def nickname(self, obj):
        return obj.profile.nickname

    def sex(self, obj):
        return obj.profile.get_sex_display()

    def vip(self, obj):
        try:
            return obj.profile.vip.vip_type
        except AttributeError:
            return "-"

    list_display = ("username", "last_login", "nickname", "sex", "vip")

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

admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
