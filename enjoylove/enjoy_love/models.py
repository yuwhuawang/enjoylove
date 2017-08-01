# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.contrib.auth.models
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.


class Profile(models.Model):
    GENDER_CHOICES = ((0, '不详'), (1,'男') , (2, '女'))
    EDUCATION_CHOICES = ((0, "小学"), (1, "中学"), (2,"大学"), (3,"硕士研究生"), (4,"博士研究生"))
    INCOME_CHOICES = ((0, "0-5"), (1, "6-10"), (2,"11-15"), (3,"16-20"), (4,"20+"))
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=15, blank=True)
    sex = models.SmallIntegerField('性别', choices=GENDER_CHOICES)
    person_intro = models.TextField('个人简介', max_length=1000, null=True, blank=True)
    birth_date = models.DateField('出生日期', null=True, blank=True)
    work_area_name = models.CharField("工作地名称", max_length=30, null=True, blank=True)
    work_area_code = models.CharField("工作地编码", max_length=15, null=True, blank=True)
    born_area_name = models.CharField("籍贯名称", max_length= 30, null=True, blank=True)
    born_area_code = models.CharField("籍贯编码", max_length= 30, null=True, blank=True)
    height = models.IntegerField("身高", null=True, blank=True)
    education = models.SmallIntegerField("学历", choices=EDUCATION_CHOICES)
    career = models.CharField("职业", max_length=50, null=True, blank=True)
    income = models.SmallIntegerField("年收入", choices=INCOME_CHOICES, null=True, blank=True)
    

    bio = models.TextField(max_length=500, blank=True)

    verify_code = models.IntegerField(null=True, blank=True, help_text="验证码")
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()