# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.views import APIView
from django.db import transaction
from django.shortcuts import render

from enjoylove.enjoy_love.api_result import ApiResult, BusinessError
from enjoylove.enjoy_orders.alipay import alipay, alipay_config
from models import Orders, Goods
from enjoy_love.models import User
#from weixinpay import WeixinBaseUtil, WeixinNotifyUtil, WeixinUtil
#from alipay import AlipayMobileBaseUtil
from weixinpay import weixinpay_config, weixinpay
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
        pay_type = request.POST.get("pay_type")
        count = request.POST.get("count")

        good = Goods.objects.get(gid=gid)
        user = User.objects.get(pk=uid)
        if pay_type == "weixin":
            notify_url = weixinpay_config.NOTIFY_URL
        elif pay_type == "alipay":
            notify_url = alipay_config.NOTIFY_URL

        order = Orders.objects.create(
            good=good,
            product_name="{}_{}".format(user.username, good.name),
            user=user,
            count=count,
            amount=good.price_actual*count,
            platform=platform,
            pay_type=pay_type,
            notify_url=notify_url,
        )

        if pay_type == "weixin":
            res = weixinpay.make_payment_request_wx(request=request,
                                              out_trade_no=order.oid,
                                              total_fee=order.amount)

        if pay_type == "alipay":
            res = alipay.make_payment_request_ali(notify_url=alipay_config.NOTIFY_URL,
                                                  out_trade_no=order.oid,
                                                  total_fee=order.amount)
        return ApiResult(result=res)


class WeixinNotifyView(APIView):
    """
    微信回调处理
    """

    def post(self, request):
        res = weixinpay.weixinpay_call_back(request)
        if res:
            try:
                order = Orders.objects.get(out_trade_no=res.get("out_trade_no", None))
                if order.oid.
            except Orders.DoesNotExist:
                pass





















