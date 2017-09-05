# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from enjoy_love.api_result import BusinessError


class Post(models.Model):
    class Meta:
        verbose_name = "帖子"
        verbose_name_plural = "帖子"
        ordering = ('-create_time', )

    CATELOG_CHOICES = (
        ("p", "帖子"),
        ("a", "文章"),
        ("e", "活动")
    )

    title = models.CharField("标题", max_length=255, blank=True, null=True)
    content = models.TextField("内容", blank=True, null=True)
    author = models.ForeignKey(User, related_name="post", related_query_name="post")
    catelog = models.SmallIntegerField("类型", choices=CATELOG_CHOICES, null=True, blank=True)
    read_count = models.IntegerField("阅读量", null=True, blank=True)
    comment_count = models.IntegerField("评论数量", null=True, blank=True)
    like_count = models.IntegerField("喜欢数量" ,null=True, blank=True)
    on_top = models.BooleanField("是否置顶", default=False)
    create_time = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.author.profile.can_post:
            raise BusinessError("您无权发布帖子")
        super(Post, self).save(*args, **kwargs)


class PostLikeRecord(models.Model):

    user = models.ForeignKey(User)
    post = models.ForeignKey(Post)
    status = models.BooleanField("是否有效", default=True)
    create_time = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    content = models.CharField("内容", max_length=255, blank=True, null=True)
    user = models.ForeignKey(User, related_name="comment", related_query_name="comment")
    like_count = models.IntegerField("喜欢数量")
    post = models.ForeignKey(Post, related_name="post", related_query_name="post"),
    create_time = models.DateTimeField(auto_now_add=True)


class CommentLikeRecord(models.Model):
    user = models.ForeignKey(User)
    post = models.ForeignKey(Post)
    status = models.BooleanField("是否有效", default=True)
    create_time = models.DateTimeField(auto_now_add=True)


class Activity(models.Model):
    class Meta:
        verbose_name = "活动报名"
        verbose_name_plural = "活动报名"
        ordering = ('-create_time', )

    user = models.ForeignKey(User)
    post = models.ForeignKey(Post)
    status = models.BooleanField("是否有效", default=True)
    create_time = models.DateTimeField(auto_now_add=True)


class Catelog(models.Model):
    name = models.CharField("名称", max_length=225)