# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.contrib.auth.models
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth.models import AbstractUser, BaseUserManager, UserManager
import time
import datetime
from django.db.models.functions import ExtractYear
from DjangoUeditor.models import UEditorField

from filter import keyword_filter

# Create your models here.




'''
class User(AbstractUser):
    nickname = models.CharField('用户名', max_length=15, blank=True)
    GENDER_CHOICES = ((0, '不详'), (1, '男'), (2, '女'))
    EDUCATION_CHOICES = ((0, '未透露'), (1, "小学"), (2, "中学"), (3, "大学"), (4, "硕士研究生"), (4, "博士研究生"))
    INCOME_CHOICES = ((0, "未透露"), (1, "0-5"), (2, "6-10"), (3, "11-15"), (4, "16-20"), (5, "20+"))
    MARRIAGE_CHOICES = ((0, '未透露'), (1, '未婚'), (2, '已婚'), (3, '离异'), (4, '丧偶'))
    CHILDREN_CHOICES = ((0, '未透露'), (1, '无'), (2, '有'))
    #user = models.OneToOneField(User, on_delete=models.CASCADE)
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
    # create_time = models.DateTimeField(auto_now_add=True)
    # update_time = models.DateTimeField(auto_now=True)
    # login_time = models.DateTimeField(auto_now_add=True)
    vip = models.ForeignKey("Vip", on_delete=models.CASCADE, null=True, blank=True)
    vip_expire_date = models.DateField("会员过期日期", null=True, blank=True)
    identity_verified = models.BooleanField("身份认证", default=False)
    has_car = models.BooleanField("是否购车", default=False)
    has_house = models.BooleanField("是否购房", default=False)
    relationship_desc = models.TextField("情感经历", null=True, blank=True)
    mate_preference = models.TextField("择偶标准", null=True, blank=True)
'''


class Profile(models.Model):
    GENDER_CHOICES = ((0, '不详'), (1, '男'), (2, '女'))
    EDUCATION_CHOICES = ((0, '未透露'),  (1, "高中"), (2, "大专"), (3, "本科"), (4, "硕士研究生"), (5, "博士研究生"))
    INCOME_CHOICES = ((0, "未透露"),  (1, "3k以下"), (2, "3k-5k"), (3, "58k"), (4, "8k-12k"), (5, "12k-20k"), (6, "20k-30k"), (7, "30k以上"))
    MARRIAGE_CHOICES = ((0, '未透露'), (1, '未婚'), (2, '离异'), (3, '丧偶'), )
    CHILDREN_CAR_HOUSE_CHOICES = ((0, '未透露'), (1, '无'), (2, '有'))
    EXPECT_MARRY_TIME = ((0, '未透露'), (1, '半年内'), (2, '一年内'))
    CAREER_CHOICES = ((0, "未透露"), (1, "在校学生"), (2, "私营业主"), (3, "农业劳动者"), (4, "企业职工"), (5, "政府机关/事业单位"), (6, "自由职业"))
    CONSTELLATIONS = ((0, "未透露"), (1, "白羊座"), (2, "金牛座"), (3, "双子座"), (4, "巨蟹座"), (5, "狮子座"), (6, "处女座"), (7, "天秤座"),
                      (8, "天蝎座"), (9, "射手座"), (10, "摩羯座"), (11, "水瓶座"), (12, "双鱼座"))

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #person_id = models.AutoField()
    nickname = models.CharField('用户名', max_length=15, null=True, blank=True, unique=True)
    sex = models.SmallIntegerField('性别', choices=GENDER_CHOICES, default=0)
    person_intro = UEditorField("个人简介",null=True, blank=True)
    #person_intro = models.TextField('个人简介',  max_length=1000, null=True, blank=True)
    birth_date = models.DateField('出生日期', null=True, blank=True)
    work_area_name = models.CharField("工作地名称", max_length=30, null=True, blank=True)
    work_area_code = models.CharField("工作地编码", max_length=15, null=True, blank=True)
    born_area_name = models.CharField("籍贯名称", max_length=30, null=True, blank=True)
    born_area_code = models.CharField("籍贯编码", max_length=30, null=True, blank=True)
    height = models.IntegerField("身高", null=True, blank=True)
    education = models.SmallIntegerField("学历", choices=EDUCATION_CHOICES, default=0)
    career = models.SmallIntegerField("职业", choices=CAREER_CHOICES, default=0)
    income = models.SmallIntegerField("月收入", choices=INCOME_CHOICES, default=0)
    expect_marry_date = models.SmallIntegerField("期望结婚时间", choices=EXPECT_MARRY_TIME, default=0)
    nationality = models.CharField("民族", max_length=15, null=True, blank=True)
    marriage_status = models.SmallIntegerField("婚姻状况", choices=MARRIAGE_CHOICES, default=0)
    birth_index = models.IntegerField("家中排行", null=True, blank=True)
    has_children = models.SmallIntegerField("有无子女", choices=CHILDREN_CAR_HOUSE_CHOICES, default=0)
    weight = models.IntegerField("体重", null=True, blank=True, help_text="单位(KG)")
    avatar = models.URLField("头像", null=True, blank=True)
    vip = models.ForeignKey("Vip", on_delete=models.CASCADE, null=True, blank=True)
    vip_expire_date = models.DateField("会员过期日期", null=True, blank=True)
    identity_verified = models.BooleanField("身份认证", default=False)
    has_car = models.SmallIntegerField("是否购车", choices=CHILDREN_CAR_HOUSE_CHOICES, default=0)
    has_house = models.SmallIntegerField("是否购房", choices=CHILDREN_CAR_HOUSE_CHOICES, default=0)
    relationship_desc = models.TextField("情感经历", null=True, blank=True)
    mate_preference = models.TextField("择偶标准", null=True, blank=True)
    constellation = models.SmallIntegerField("星座", choices=CONSTELLATIONS, default=0)
    on_top = models.BooleanField("是否置顶", default=False)
    age = models.IntegerField("年龄", default=0, blank=True)
    like = models.IntegerField("心动人数", default=0)

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

        if self.birth_date:
            current_year = int(time.strftime('%Y', time.localtime(time.time())))
            if isinstance(self.birth_date, datetime.date):
                born_year = self.birth_date.year
            else:
                born_year = int(datetime.datetime.strptime(self.birth_date, "%Y-%m-%d").year)
            self.age = current_year - born_year

        super(Profile, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.username

    def __unicode__(self):
        return self.user.username


class FilterControl(models.Model):
    class Meta:
        verbose_name = "首页筛选条件"
        verbose_name_plural = "首页筛选条件"

    name = models.CharField("筛选条件", max_length=20)
    param = models.CharField("筛选参数", max_length=20)
    valid = models.BooleanField("是否有效", default=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class FilterOptions(models.Model):
    class Meta:
        verbose_name = "筛选选项"
        verbose_name_plural = "筛选选项"

    filter = models.ForeignKey("FilterControl",  on_delete=models.CASCADE, related_name="filter_options", related_query_name="filter_options")
    option_name = models.CharField("选项名称", max_length=20)
    option_value = models.CharField("选项值", max_length=20)

    def __str__(self):
        return self.option_name

    def __unicode__(self):
        return self.option_name


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


class ContactType(models.Model):
    class Meta:
        verbose_name = "联系方式"
        verbose_name_plural = "联系方式"

    name = models.CharField("信息类型", max_length=25)
    valid = models.BooleanField("是否有效", default=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class UserContact(models.Model):

    class Meta:
        verbose_name = "个人通讯信息"
        verbose_name_plural = "个人通讯信息"
        unique_together = ("user", "type")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contacts", related_query_name="contacts")
    type = models.ForeignKey("ContactType", verbose_name="联系方式", on_delete=models.CASCADE, related_name="contacts", related_query_name="contacts")
    content = models.CharField("联系方式内容", max_length=20)
    deleted = models.BooleanField("是否删除", default=False)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.type.name

    def __unicode__(self):
        return self.type.name


class PersonalTag(models.Model):
    class Meta:
        verbose_name = "个人标签"
        verbose_name_plural = "个人标签"

    name = models.CharField("个人标签", max_length=20)
    valid = models.BooleanField("是否有效", default=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class UserTags(models.Model):
    class Meta:
        verbose_name = "用户标签"
        verbose_name_plural = "用户标签"
        unique_together = ("user", "tag")
    user = models.ForeignKey(User, verbose_name="标签", on_delete=models.CASCADE, related_name="tags", related_query_name="tags")
    tag = models.ForeignKey(PersonalTag, related_name="tags", related_query_name="tags")
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.tag.name

    def __unicode__(self):
        return self.tag.name


class PersonalInterest(models.Model):
    class Meta:
        verbose_name = "兴趣爱好设置"
        verbose_name_plural = "兴趣爱好设置"

    name = models.CharField("兴趣爱好", max_length=20)
    valid = models.BooleanField("是否有效", default=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class UserInterest(models.Model):

    class Meta:
        verbose_name = "兴趣爱好"
        verbose_name_plural = "兴趣爱好"
        unique_together = ("user", "interest")

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="interest", related_query_name="interest")
    interest = models.ForeignKey("PersonalInterest", on_delete=models.CASCADE, related_name="interest", related_query_name="interest", verbose_name="兴趣")
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.interest.name

    def __unicode__(self):
        return self.interest.name


class Album(models.Model):
    class Meta:
        verbose_name = "相册"
        verbose_name_plural = "相册"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="albums", related_query_name="albums",)
    photo_url = models.TextField("图片地址")
    upload_time = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField("是否删除", default=False)
    delete_time = models.DateTimeField(null=True)

    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return unicode(self.id)


class IdentityVerify(models.Model):

    class Meta:
        verbose_name = "身份认证"
        verbose_name_plural = "身份认证"
    STATUS = ((0, "待审核"), (1, "已同意"), (2, "已拒绝"))

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="identity", related_query_name="identity",)
    real_name = models.CharField("真实姓名", max_length=20)
    id_number = models.CharField("身份证号", max_length=20)
    img_front = models.URLField("正面身份证")
    img_back = models.URLField("背面身份证")
    status = models.SmallIntegerField("审核状态", choices=STATUS, default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class GlobalSettings(models.Model):
    class Meta:
        verbose_name = "app设置"
        verbose_name_plural = "app设置"
    key = models.CharField("名称", max_length=20)
    value = models.CharField("值", max_length= 100)
    valid = models.BooleanField("是否有效", default=True)


class Advertisement(models.Model):
    class Meta:
        verbose_name = "广告设置"
        verbose_name_plural = "广告设置"

    SHOW_PLACE_CHOISES=((0, "所有位置"), (1, "人物列表页"), (2, "文章列表页"))
    name = models.CharField("广告条目", max_length=25)
    desc = models.TextField("广告文字")
    img = models.TextField("图片")
    url = models.URLField("跳转地址")
    valid = models.BooleanField("是否有效", default=True)
    expire_time = models.DateTimeField("过期时间", null=True)
    show_place = models.SmallIntegerField("展示的tab", choices=SHOW_PLACE_CHOISES)
    show_page = models.IntegerField("展示的页数", default=1)
    show_position = models.IntegerField("展示的位置", default=10)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class LikeRecord(models.Model):
    class Meta:
        verbose_name = "心动记录"
        verbose_name_plural = "心动记录"
        unique_together = ("like_from", "like_to")
    like_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likerecord", related_query_name="likerecord")
    like_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="liketorecord", related_query_name="liketorecord")
    #valid = models.BooleanField("是否有效", default=True)
    create_time = models.DateTimeField(auto_now_add=True)


class UserMessage(models.Model):
    class Meta:
        verbose_name = "留言"
        verbose_name_plural = "留言"

    message_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages_from", related_query_name="messages_from")
    message_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages_to", related_query_name="messages_to")
    content = models.TextField("留言内容")
    deleted = models.BooleanField("是否删除", default=False)
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[0:10]

    def __unicode__(self):
        return self.content[0:10]

    def save(self, *args, **kwargs):

        self.content = keyword_filter.filter(self.content)
        super(UserMessage, self).save(*args, **kwargs)


class ContactExchange(models.Model):
    EXCHANGE_STATUS = ((0, "待处理"), (1, "同意"), (2, "拒绝"))

    class Meta:
        verbose_name = "联系方式交换记录"
        verbose_name_plural = "联系方式交换记录"
        unique_together = ("exchange_sender", "exchange_receiver", "exchange_type" )
    exchange_sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="exchange_sender", related_query_name ="exchange_sender")
    exchange_receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="exchange_receiver", related_query_name ="exchange_receiver")
    exchange_type = models.ForeignKey(ContactType, on_delete=models.CASCADE, related_name="exchange_type", related_query_name ="exchange_type")
    exchange_status = models.SmallIntegerField("状态", choices=EXCHANGE_STATUS, default=0)

    def __str__(self):
        return self.exchange_type.name

    def __unicode__(self):
        return self.exchange_type.name


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile()
        profile.user = instance
        profile.save()

post_save.connect(create_user_profile, User)


@receiver(post_save, sender=IdentityVerify, )
def update_verify_status(sender, instance, **kwargs):
    user = User.objects.get(pk=instance.user.id)
    if instance.status == 1:
        user.profile.identity_verified = True
        user.profile.save()
    else:
        user.profile.identity_verified = False
        user.profile.save()



