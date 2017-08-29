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
from models import RECEIPT_STATE_READY, RECEIPT_STATE_NOTIFY_RECEIVED, RECEIPT_STATE_PARTNER_NOTIFY_PROCESSED, RECEIPT_STATE_FINISHED, \
    RECEIPT_STATUS_READY, RECEIPT_STATUS_SUCCEED, RECEIPT_STATUS_FAILURE,RECEIPT_STATUS_CLOSED

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
        notify_url = ""
        if pay_type == "weixin":
            notify_url = weixinpay_config.NOTIFY_URL
        elif pay_type == "alipay":
            notify_url = alipay_config.NOTIFY_URL

        order = Orders.objects.create(
            good=good,
            product_name="{}_{}".format(user.username, good.name),
            user=user,
            count=count,
            amount=good.price_actual*count*100,
            platform=platform,
            pay_type=pay_type,
            notify_url=notify_url,
        )
        res = dict()
        if pay_type == "weixin":
            res = weixinpay.make_payment_request_wx(request=request,
                                              out_trade_no=order.oid,
                                              total_fee=order.amount)

        if pay_type == "alipay":
            res = alipay.make_payment_request_ali(out_trade_no=order.oid,
                                                  total_fee=order.amount)
        return ApiResult(result=res)


class WeixinNotifyView(APIView):
    """
    微信回调处理
    """
    def post(self, request):
        res = weixinpay.weixinpay_call_back(request)

        if not res:
            return weixinpay.weixinpay_response_xml("FAIL")
        if res:
            try:
                order = Orders.objects.get(out_trade_no=res.get("out_trade_no", None))
                if order.state == RECEIPT_STATE_READY:
                    order.state = RECEIPT_STATE_NOTIFY_RECEIVED
                    order.save()
                    if res["result_code"] == "SUCCESS":
                        order.state = RECEIPT_STATE_FINISHED
                        if res['total_fee'] == order.amount:
                            order.state = RECEIPT_STATE_FINISHED
                            order.status = RECEIPT_STATUS_SUCCEED
                        else:
                            order.state = RECEIPT_STATE_FINISHED
                            order.status = RECEIPT_STATUS_FAILURE
                        order.save()
                        return weixinpay.weixinpay_response_xml("SUCCESS")
                elif order.state == RECEIPT_STATE_FINISHED:
                    return weixinpay.weixinpay_response_xml("SUCCESS")
            except Orders.DoesNotExist:
                    return weixinpay.weixinpay_response_xml("FAIL")


class AlipayNotifyView(APIView):
    """
    支付宝回调处理
    """

    def post(self, request):
        res = alipay.alipay_call_back(request)


class NotifyView(APIView):

    authentication_classes = ()

    @transaction.commit_manually
    def get(self, request, source=None):
        try:

            util = NotifyUtil.fromRequest(request, source)

            # signature is ok and parameters is provided
            if not util.isValid():
                transaction.rollback()
                return HttpResponse('Invalid parameters', status=400)
            if not util.isSucceed():
                transaction.rollback()
                return HttpResponse(util.getSuccessMessage())

            # persist the notify for furture usage
            notify = util.persistNotify()
        except Exception as ex:
            logger.error('failed to veirfy notify, exception: %s', ex)
            transaction.rollback()
            return HttpResponse('Invalid parameters', status=400)

        # commit data to database to make sure data will not lost
        try:
            transaction.commit()

            util.delayProcessNotify(notify)
            return HttpResponse(util.getSuccessMessage())
        except transaction.TransactionManagementError as ex:
            logger.error('failed to commit data, exception: %s', ex)
            transaction.rollback()
            return HttpResponse(util.getErrorMessage())
        except Exception as ex:
            logger.error('failed to process notify, exception: %s', ex)
            transaction.rollback()
            return HttpResponse(util.getErrorMessage())

    def post(self, request, source=None):
        return self.get(request, source)














