# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.contrib.auth.models import User
from models import Profile

# Register your models here.


class ProfileInline(admin.StackedInline):
    model = Profile
    verbose_name = 'profile'


class UserProfileAdmin(admin.ModelAdmin):
    inlines = (ProfileInline,)


admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)