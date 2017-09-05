# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from models import Orders

# Register your models here.


@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):

    def uid(self, obj):
        return obj.user.id

    def nickname(self, obj):
        return obj.user.profile.nickname



    list_display = ("oid", "uid", "nickname",)
    #list_filter = ("valid", )
    nickname.short_description = "昵称"
