# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.views import APIView
from django.db import transaction
from django.shortcuts import render

# Create your views here.


class OrderCreateView(APIView):
    """
    创建订单
    """
    @transaction.atomic
    def post(self, request):
        uid = request.POST.get("uid")
        gid = request.POST.get("gid")
        platform = request.META.get("platform")
        notify_url = request.POST.get("notify_url")




