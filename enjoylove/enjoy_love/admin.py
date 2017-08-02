# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.contrib.auth.models import User
from models import Profile, UserExtensions

# Register your models here.


class ProfileInline(admin.StackedInline):
    model = Profile
    verbose_name = 'profile'


class UserExtensionInline(admin.StackedInline):
    model = UserExtensions
    verbose_name = 'userextensions'


class UserProfileAdmin(admin.ModelAdmin):
    inlines = (ProfileInline, UserExtensionInline, )


admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)