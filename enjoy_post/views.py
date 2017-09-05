# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import transaction
from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView

from enjoy_love.api_result import ApiResult, BusinessError
from models import Post, PostLikeRecord


class CreatePostView(APIView):

    def post(self, request):
        uid = request.POST.get("uid")
        content = request.POST.get("content")

        try:
            Post.objects.create(
                author_id=uid,
                content=content,
                catalog=Post.POSTS
            )
        except BusinessError as be:
            return be
            #return BusinessError("您无权发布帖子")
        return ApiResult()


class SetPostLikeView(APIView):
    @transaction.atomic
    def post(self, request):
        uid = request.POST.get("uid")
        post_id = int(request.POST.get("pid"))
        action = int(request.POST.get("action"))

        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return BusinessError("该帖子不存在")

        if action == 0:
            try:
                post_like = PostLikeRecord.objects.get(post_id=post_id,
                                                   user_id=uid)
                if post_like.status == 0:
                    return BusinessError("您未赞过该帖子")
                post_like.status = 0
                post_like.save()
                post.like_count -= 1
                post.save()
                return ApiResult()
            except PostLikeRecord.DoesNotExist:
                return ApiResult()

        elif action == 1:
            try:
                post_like = PostLikeRecord.objects.get(post_id=post_id,
                                                   user_id=uid)
                if post_like.status == 1:
                    return BusinessError("您已经赞过该帖子")
                post_like.status = 1
                post_like.save()
                post.like_count += 1
                post.save()
                return ApiResult()
            except PostLikeRecord.DoesNotExist:
                PostLikeRecord.objects.create(
                    post_id=post_id,
                    user_id=uid
                )
                post.like_count += 1
                post.save()
                return ApiResult()
        else:
            return BusinessError("bad request")

