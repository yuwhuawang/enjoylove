# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from models import Post


class CreatePostView(APIView):

    def post(self, request):
        uid = request.POST.get("uid")
        content = request.POST.get("content")
        post = Post()
        post.author.id = uid
        post.author.content = content
        post.save()


