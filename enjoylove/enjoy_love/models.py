# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.contrib.auth.models
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.


class Profile(models.Model):
    GENDER_CHOICES = ((0, '不详'), (1, '男'), (2, '女'))
    EDUCATION_CHOICES = ((0, '未透露'),  (1, "小学"), (2, "中学"), (3, "大学"), (4, "硕士研究生"), (4, "博士研究生"))
    INCOME_CHOICES = ((0, "未透露"),  (1, "0-5"), (2, "6-10"), (3, "11-15"), (4, "16-20"), (5, "20+"))
    MARRIAGE_CHOICES = ((0, '未透露'), (1, '未婚'), (2, '已婚'), (3, '离异'), (4, '丧偶'))
    CHILDREN_CHOICES = ((0, '未透露'), (1, '无'), (2, '有'))
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField('用户名', max_length=15, blank=True)
    sex = models.SmallIntegerField('性别', choices=GENDER_CHOICES, default=0)
    person_intro = models.TextField('个人简介', max_length=1000, null=True, blank=True)
    birth_date = models.DateField('出生日期', null=True, blank=True)
    work_area_name = models.CharField("工作地名称", max_length=30, null=True, blank=True)
    work_area_code = models.CharField("工作地编码", max_length=15, null=True, blank=True)
    born_area_name = models.CharField("籍贯名称", max_length=30, null=True, blank=True)
    born_area_code = models.CharField("籍贯编码", max_length=30, null=True, blank=True)
    height = models.IntegerField("身高", null=True, blank=True)
    education = models.SmallIntegerField("学历", choices=EDUCATION_CHOICES, default=0)
    career = models.CharField("职业", max_length=50, null=True, blank=True)
    income = models.SmallIntegerField("年收入", choices=INCOME_CHOICES, default=0)
    expect_marry_date = models.DateField("期望结婚时间", null=True, blank=True)
    nationality = models.CharField("民族", max_length=15, null=True, blank=True)
    marriage_status = models.SmallIntegerField("婚姻状况", choices=MARRIAGE_CHOICES, default=0)
    birth_index = models.IntegerField("家中排行", null=True, blank=True)
    has_children = models.SmallIntegerField("有无子女", choices=CHILDREN_CHOICES, default=0)
    weight = models.IntegerField("体重", null=True, blank=True, help_text="单位(KG)")
    avatar = models.TextField("头像", null=True, blank=True)
    #create_time = models.DateTimeField(auto_now_add=True)
    #update_time = models.DateTimeField(auto_now=True)
    #login_time = models.DateTimeField(auto_now_add=True)
    vip = models.ForeignKey("Vip", on_delete=models.CASCADE, null=True, blank=True)
    vip_expire_date = models.DateField("会员过期日期", null=True, blank=True)
    identity_verified = models.BooleanField("身份认证", default=False)
    has_car = models.BooleanField("是否购车", default=False)
    has_house = models.BooleanField("是否购房", default=False)
    relationship_desc = models.TextField("情感经历", null=True, blank=True)
    mate_preference = models.TextField("择偶标准", null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            try:
                p = Profile.objects.get(user=self.user)
                self.pk = p.pk
            except Profile.DoesNotExist:
                pass

        if self.vip is None:  # Set default reference
            try:
                self.vip = Vip.objects.get(id=1)
            except:
                pass
        super(Profile, self).save(*args, **kwargs)


class Vip(models.Model):
    class Meta:
        verbose_name = "会员"
        verbose_name_plural = "会员"

    vip_type = models.CharField(max_length=20)
    vip_month_price = models.DecimalField("单月会员价", max_digits=20, decimal_places=2, blank=True, null=True)
    vip_month_price_org = models.DecimalField("单月会员价原价", max_digits=20, decimal_places=2, blank=True, null=True)
    vip_half_year_price = models.DecimalField("半年会员价", max_digits=20, decimal_places=2, blank=True, null=True)
    vip_half_year_price_org = models.DecimalField("半年会员价原价", max_digits=20, decimal_places=2, blank=True, null=True)
    vip_year_price = models.DecimalField("一年会员价", max_digits=20, decimal_places=2, blank=True, null=True)
    vip_year_price_org = models.DecimalField("一年会员价原价", max_digits=20, decimal_places=2, blank=True, null=True)
    vip_member_count = models.IntegerField("vip用户数量", blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vip_type

    def __unicode__(self):
        return self.vip_type


class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contact", related_query_name="contact")
    type = models.CharField("联系方式类型", max_length=20)
    content = models.CharField("联系方式内容", max_length=20)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class PersonalTag(models.Model):
    name = models.CharField("个人标签", max_length=20)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class UserTags(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tags", related_query_name="tags")
    tag = models.CharField(max_length=20)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class PersonalInterest(models.Model):
    name = models.CharField("兴趣爱好", max_length=20)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class UserInterest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="interest", related_query_name="interest")
    interest = models.CharField(max_length=20)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class Album(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="albums", related_query_name="albums",)
    photo_url = models.URLField("图片地址")
    upload_time = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField("是否删除", default=False)
    delete_time = models.DateTimeField()


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile()
        profile.user = instance
        profile.save()

post_save.connect(create_user_profile, User)

